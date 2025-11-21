
<p align="center">
  <img width="450" height="450" src="https://github.com/user-attachments/assets/91c86a7d-9a2f-4fc0-a0eb-4eba09bbc485" />
</p>


# knock-knock
 
A Python CLI tool to set reminders for GMRT observation slots. Never miss your telescope time again.
 
## Installation
 
```bash
pip install knock-knock
```
 
## Usage
 
Create a reminder for your GMRT observation:
 
```bash
knock-knock create <GMRT_SCHEDULE_URL>
```
 
You'll be prompted for your email and name. The system will:
- Extract observation details from the GMRT schedule
- Store your reminder in a centralized system
- Send you email reminders at 3 days and 1 day before your observation

## Requirements
 
- Python 3.7+
- Active email address
- GMRT schedule URL with your observation details
 
## Email Schedule
 
- First reminder: 3 days before observation
- Final reminder: 1 day before observation
 
## Copyright
 
Copyright (c) 2025 Arpan Pal
 
Developed by Arpan Pal — after forgetting an observation slot and getting thoroughly scolded by my operator friends Arun, Tanuja, and Manthan. So, to avoid that happening again, I built this tool. If it helps you too, that's a bonus.
 
## License
 
MIT

## Disclaimer

The software does not guarantee reminders, as it depends on GitHub workflows. It is a convenience tool and carries no legal guarantee.
