# Octopus Minmax Bot 🐙🤖

## Description
This bot will use your electricity usage and compare your current Smart tariff costs for the day with another smart tariff and initiate a switch if it's cheaper. See below for supported tariffs.

Due to how Octopus Energy's Smart tariffs work, switching manually makes the *new* tariff take effect from the start of the day. For example, if you switch at 11 PM, the whole day's costs will be recalculated based on your new tariff, allowing you to potentially save money by tariff-hopping.

I created this because I've been a long-time Agile customer who got tired of the price spikes. I now use this to enjoy the benefits of Agile (cheap days) without the risks (expensive days).

I personally have this running automatically every day at 11 PM inside a Raspberry Pi Docker container, but you can run it wherever you want.  It sends notifications and updates to a variety of services via [Apprise](https://github.com/caronc/apprise), but that's not required for it to work.

## How to Use

### Requirements
- An Octopus Energy Account  
  - In case you don't have one, we both get £50 for using my referral: https://share.octopus.energy/coral-lake-50
  - Get your API key [here](https://octopus.energy/dashboard/new/accounts/personal-details/api-access)
- A smart meter
- Be on a supported Octopus Smart Tariff (see tariffs below)
- **One of the following for consumption data:**
  - An Octopus Home Mini for real-time usage. Get one for free [here](https://octopus.energy/blog/octopus-home-mini/).
  - **OR** Home Assistant with a Shelly device and the [Octopus Energy integration](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy)

### HomeAssistant Addon

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Feelmafia%2Foctopus-minmax)

OR

To install this third-party add-on:

1. Open Home Assistant > Settings > Add-ons > Add-on Store.
2. Click the menu (three dots in the top-right corner) and select Repositories.
3. Paste the GitHub repository link into the field at the bottom:
https://github.com/eelmafia/octopus-minmax
4. Refresh the page if needed. The add-on will appear under **Octopus MinMax Bot**.


### Running Manually
1. Install the Python requirements.
2. Configure the environment variables.
3. Schedule this to run once a day with a CRON job or Docker. I recommend running it at 11 PM to leave yourself an hour as a safety margin in case Octopus takes a while to generate your new agreement.

### Running using Docker
Docker run command:
```
docker run -d \
  --name MinMaxOctopusBot \
  -e ACC_NUMBER="<your_account_number>" \
  -e API_KEY="<your_api_key>" \
  -e EXECUTION_TIME="23:00" \
  -e NOTIFICATION_URLS="<apprise_notification_urls>" \
  -e ONE_OFF=false \
  -e DRY_RUN=false \
  -e TARIFFS=go,agile,flexible \
  -e TZ=Europe/London \
  -e BATCH_NOTIFICATIONS=false \
  --restart unless-stopped \
  eelmafia/octopus-minmax-bot
```
or use the docker-compose.yaml **Don't forget to add your environment variables**

Note : Remove the --restart unless line if you set the ONE_OFF variable or it will continuously run.

#### Environment Variables

**Core Configuration:**
| Variable                    | Description                                                                                                                                                                                                             |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ACC_NUMBER`                | Your Octopus Energy account number.                                                                                                                                                                                     |
| `API_KEY`                   | API token for accessing your Octopus Energy account.                                                                                                                                                                    |
| `TARIFFS`                   | A list of tariffs to compare against. Default is go,agile,flexible                                                                                                                                                      | 
| `EXECUTION_TIME`            | (Optional) The time (HH:MM) when the script should execute. Default is `23:00` (11 PM).                                                                                                                                 |
| `NOTIFICATION_URLS`         | (Optional) A comma-separated list of [Apprise](https://github.com/caronc/apprise) notification URLs for sending logs and updates.  See [Apprise documentation](https://github.com/caronc/apprise/wiki) for URL formats. |
| `ONE_OFF`                   | (Optional) A flag for you to simply trigger an immediate execution instead of starting scheduling.                                                                                                                      |
| `DRY_RUN`                   | (optional) A flag to compare but not switch tariffs.                                                                                                                                                                    |
| `BATCH_NOTIFICATIONS`       | (optional) A flag to send messages in one batch rather than individually.                                                                                                                                               |

**Home Assistant Integration (Optional):**
| Variable                    | Description                                                                                                                                                                                                             |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `HA_URL`                    | (Optional) Home Assistant URL. Default is `http://supervisor/core/api` for HA addon, or `http://your-ha-instance:8123/api` for Docker.                                                                                |
| `HA_TOKEN`                  | (Optional) Home Assistant long-lived access token. Required if using HA integration.                                                                                                                                   |
| `HA_ENERGY_ENTITY`          | (Optional) Entity ID for your Shelly energy sensor (e.g., `sensor.shelly_energy_today`). If provided, uses HA instead of Octopus Mini.                                                                               |
| `HA_RATE_ENTITY`            | (Optional) Entity ID for Octopus Energy rate sensor from the HA integration (e.g., `sensor.octopus_energy_electricity_..._current_rate`).                                                                            |
| `HA_STANDING_CHARGE_ENTITY` | (Optional) Entity ID for Octopus Energy standing charge sensor from the HA integration (e.g., `sensor.octopus_energy_electricity_..._standing_charge`).                                                              |

#### Supported Tariffs

Below is a list of supported tariffs, their IDs (to use in environment variables), and whether they are switchable.

**None switchable tariffs are use for PRICE COMPARISON ONLY**

| Tariff Name      | Tariff ID | Switchable |
|------------------|-----------|------------|
| Flexible Octopus | flexible  | ❌          |
| Agile Octopus    | agile     | ✅          |
| Cosy Octopus     | cosy      | ✅          |
| Octopus Go       | go        | ✅          |


#### Setting up Apprise Notifications

The `NOTIFICATION_URLS` environment variable allows you to configure notifications using the powerful [Apprise](https://github.com/caronc/apprise) library.  Apprise supports a wide variety of notification services, including Discord, Telegram, Slack, email, and many more.

To configure notifications:

1.  **Determine your desired notification services:**  Decide which services you want to receive notifications on (e.g., Discord, Telegram).

2.  **Find the Apprise URL format for each service:**  Consult the [Apprise documentation](https://github.com/caronc/apprise/wiki) to find the correct URL format for each service you've chosen.  For example:

    *   **Discord:** `discord://webhook_id/webhook_token`
    *   **Telegram:** `tgram://bottoken/ChatID`

3.  **Set the `NOTIFICATION_URLS` environment variable:** Create a comma-separated string containing the Apprise URLs for all your desired services.  For example:

    ```bash
    NOTIFICATION_URLS="discord://webhook_id/webhook_token,tgram://bottoken/ChatID,mailto://user:pass@example.com?to=recipient@example.com"
    ```

    Make sure to replace the example values with your actual credentials.

4.  **Restart the container (if using Docker) or run the script:**  The bot will now send notifications to all the configured services.

## Home Assistant Integration

The bot now supports using Home Assistant as an alternative to the Octopus Home Mini for consumption data. This is particularly useful if you have a Shelly device or other energy monitor integrated with Home Assistant.

### Prerequisites

1. **Home Assistant** with the [Octopus Energy integration](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy) installed
2. **Shelly device** (or similar energy monitor) providing consumption data to Home Assistant
3. **Long-lived access token** for Home Assistant API access

### Setup Steps

1. **Install the Octopus Energy HA Integration:**
   - Follow the instructions at https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy
   - This provides rate and standing charge entities

2. **Find Your Entity IDs:**
   - **Energy Entity:** Your Shelly energy sensor (e.g., `sensor.shelly_energy_today`)
   - **Rate Entity:** From Octopus integration (e.g., `sensor.octopus_energy_electricity_z14qu60479_1800024395880_current_rate`)
   - **Standing Charge Entity:** From Octopus integration (e.g., `sensor.octopus_energy_electricity_z14qu60479_1800024395880_standing_charge`)

3. **Create a Long-Lived Access Token:**
   - Go to Home Assistant > Profile > Long-Lived Access Tokens
   - Create a new token and copy it

4. **Configure the Bot:**
   - **For Home Assistant Addon:** Fill in the HA integration fields in the addon configuration
   - **For Docker:** Add the HA environment variables to your docker-compose.yaml or docker run command

### How It Works

When Home Assistant entities are configured:
- The bot fetches historical energy data from your Shelly device
- Calculates 30-minute consumption periods
- Gets corresponding rate data from the Octopus Energy integration
- Calculates costs using: `consumption_kwh × rate_£_per_kwh × 1.05 (VAT) × 100 (pence)`
- Uses the standing charge from the Octopus Energy integration

This provides more accurate consumption data than the Octopus Mini estimates, while still using official Octopus rates for cost calculations.

### Fallback Behavior

If Home Assistant is unavailable or misconfigured, the bot automatically falls back to using the Octopus Mini data source, ensuring reliability.

### Testing Your Setup

A test script is provided to verify your Home Assistant integration:

```bash
python test_ha_integration.py
```

This script will:
- Check your configuration
- Test connectivity to Home Assistant
- Verify entity availability
- Show sample consumption and cost data
- Confirm the data source factory is working correctly

Run this before deploying to ensure everything is configured properly.
