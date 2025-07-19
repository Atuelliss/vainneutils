## Purpose of the Cog

- This cog allows the Server Owner to track and manage Player-hosted Events, including a deposit balance that can be set at your preference(default is 2500) for Admin-involvement. There are various admin subcommands to control who can make deposits, completing the events and updating appropriate tallies, and canceling events with or without refunds based on Admin input.

# Advanced Cookiecutter Template Used

This cog template is a more advanced version of the simple cog template. It includes a more robust structure for larger cogs, and utilizes Pydantic to objectify config data so that youre not messing around with dictionaries all the time. It also uses its own file store instead of Red's config.

## Key Components

- Subclassed commands, listeners, and tasks
- Pydantic "database" management
- Conservative i/o writes to disk
- Non blocking `self.save()` method

## Admin Commands

- [p]pevent - All Admin commands are subcommands of this one.
-  Subcommands are: add, allow, ban, cancel, complete, list, remove, setdeposit, unban.

## Player Commands

- [p]pdeposit - No argument, confirms the user is allowed to make a deposit, and then asks them to confirm they want to before taking the redbot bank balance away and marking their deposit as secure.

- [p]mypevents - Aliased to [p]mypevent and [p]myevents, Shows the user their specific information. Does not permit them to view others.

