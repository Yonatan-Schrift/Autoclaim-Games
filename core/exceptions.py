"""
@file:   core/exceptions.py
@module: core.exceptions
@brief:  Custom exception hierarchy for the project.
         All exceptions inherit from ProjectError so they can be caught together.
@author: Yonatan-Schrift
"""

INVALID_CREDS_MSG = (
    "Your credentials are invalid, please check your user.env and update it with correct credentials. "
    "If you are sure they're correct, create an issue on GitHub."
)


class ProjectError(Exception):
    """Base class for all custom errors."""
    pass


class InvalidCredentialsError(ProjectError):
    """Raised when credentials are invalid."""
    pass


class LocatorNotFoundError(ProjectError):
    """Raised when a required UI locator is not found on the page."""
    pass


class MissingValueError(ProjectError):
    """Raised when a required value is missing."""
    pass


class EpicGamesGameNotFoundError(ProjectError):
    """Raised when a game name is not found. Specific to Epic-Games"""
    pass

class AccountNotLinkedError(ProjectError):
    """Raised when an account is not linked. Specific to Prime-Gaming"""
    pass