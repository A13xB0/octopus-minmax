#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v yq &> /dev/null; then
        print_warning "yq is not installed. Attempting to extract version using grep/sed..."
        USE_YQ=false
    else
        USE_YQ=true
    fi
}

# Extract version from config.yaml
get_version() {
    if [ "$USE_YQ" = true ]; then
        VERSION=$(yq eval '.version' octopus_minmax_bot_addon/config.yaml)
    else
        # Fallback method using grep and sed
        VERSION=$(grep '^version:' octopus_minmax_bot_addon/config.yaml | sed 's/version: *//' | tr -d '"' | tr -d "'")
    fi
    
    if [ -z "$VERSION" ]; then
        print_error "Could not extract version from octopus_minmax_bot_addon/config.yaml"
        exit 1
    fi
    
    print_status "Extracted version: $VERSION"
}

# Docker image details
DOCKER_REPO="hectospark/octopus-minmax-bot"
ARCHITECTURES=("armhf" "armv7" "amd64" "aarch64")

# Function to map architecture to Docker platform
get_platform() {
    case "$1" in
        "armhf") echo "linux/arm/v6" ;;
        "armv7") echo "linux/arm/v7" ;;
        "amd64") echo "linux/amd64" ;;
        "aarch64") echo "linux/arm64" ;;
        *) echo "unknown" ;;
    esac
}

# Check if user is logged into Docker Hub
check_docker_login() {
    print_status "Checking Docker Hub authentication..."
    if ! docker info | grep -q "Username:"; then
        print_warning "Not logged into Docker Hub. Please run 'docker login' first."
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Build and push multi-architecture images
build_and_push() {
    print_status "Building and pushing multi-architecture Docker images..."
    print_status "Repository: $DOCKER_REPO"
    print_status "Version: $VERSION"
    print_status "Architectures: ${ARCHITECTURES[*]}"
    
    # Create buildx builder if it doesn't exist
    if ! docker buildx ls | grep -q "multiarch-builder"; then
        print_status "Creating buildx builder..."
        docker buildx create --name multiarch-builder --use
        docker buildx inspect --bootstrap
    else
        print_status "Using existing buildx builder..."
        docker buildx use multiarch-builder
    fi
    
    # Build platform string for docker buildx
    PLATFORMS=""
    for arch in "${ARCHITECTURES[@]}"; do
        if [ -n "$PLATFORMS" ]; then
            PLATFORMS="$PLATFORMS,"
        fi
        PLATFORMS="$PLATFORMS$(get_platform "$arch")"
    done
    
    print_status "Building for platforms: $PLATFORMS"
    
    # Build and push with version tag
    print_status "Building and pushing with version tag: $VERSION"
    docker buildx build \
        --platform "$PLATFORMS" \
        --tag "$DOCKER_REPO:$VERSION" \
        --tag "$DOCKER_REPO:latest" \
        --push \
        --file dockerfile \
        .
    
    print_status "Successfully built and pushed:"
    print_status "  - $DOCKER_REPO:$VERSION"
    print_status "  - $DOCKER_REPO:latest"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    # Remove the buildx builder if we created it
    if docker buildx ls | grep -q "multiarch-builder"; then
        docker buildx rm multiarch-builder || true
    fi
}

# Main execution
main() {
    print_status "Starting multi-architecture Docker build and push process..."
    
    # Set trap for cleanup on exit
    trap cleanup EXIT
    
    check_requirements
    get_version
    check_docker_login
    build_and_push
    
    print_status "Build and push process completed successfully!"
}

# Run main function
main "$@"
