// Specify the database
use("User_Behaviour");

// Now apply the update to your collection
db.getCollection("User").updateMany(
  {},
  [
    {
      $set: {
        Device: {
          Model: "$Device Model",
          OperatingSystem: "$Operating System"
        },
        UsageMetrics: {
          AppUsageTime: "$App Usage Time (min/day)",
          ScreenOnTime: "$Screen On Time (hours/day)",
          BatteryDrain: "$Battery Drain (mAh/day)",
          NumberOfAppsInstalled: "$Number of Apps Installed",
          DataUsage: "$Data Usage (MB/day)"
        }
      }
    },
    {
      $unset: [
        "Device Model",
        "Operating System",
        "App Usage Time (min/day)",
        "Screen On Time (hours/day)",
        "Battery Drain (mAh/day)",
        "Number of Apps Installed",
        "Data Usage (MB/day)"
      ]
    }
  ]
);
