# telegram_notifier
A simple python app for notifying stuff in telegram

Example of client config:

```
{
  "name": name of your client,
  "supervisor_event_listener": do you want to listen supervisor? (0 or 1),
  "client_online_timeout": set timeout for your client (seconds),
  "tasks": {
    "check_disk_usage": {
      "enable": turn on or turn off this task (0 or 1),
      "period": how often do you want to check this task (seconds),
      "arguments": {
        "filesystem": "/dev/nvme0n1p5.*" #your filesystem to check disk_usage
      }, #additional information
      "handler": {
        "handler_type": "update_parameter_by_trigger",
        "minimal_trigger": it's minimal trigger when you receive a warning message (percents),
        "trigger_step": it's a step to increment minimal trigger when it's reached (percents),
        "message_priority": it's level of message priority (1 - 5)
      }
    },
    "check_cpu_usage": {
      "enable": turn on or turn off this task (0 or 1),
      "period": how often do you want to check this task (seconds),
      "arguments": {
      }, #additional information
      "handler": {
        "handler_type": "update_parameter_by_trigger",
        "minimal_trigger": it's minimal trigger when you receive a warning message (percents),
        "message_priority": it's level of message priority (1 - 5)
      }
    },
    "check_ram_usage": {
      "enable": turn on or turn off this task (0 or 1),
      "period": how often do you want to check this task (seconds),
      "arguments": {
      }, #additional information
      "handler": {
        "handler_type": "update_parameter_by_trigger",
        "minimal_trigger": it's minimal trigger when you receive a warning message (percents),
        "trigger_step": it's a step to increment minimal trigger when it's reached (percents),
        "message_priority": it's level of message priority (1 - 5)
      }
    }
  }
}
```

