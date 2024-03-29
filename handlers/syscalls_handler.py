import handlers.handler_factory as handler_factory
from addons.syscalls.syscallinfo import *
from bottypes.command_descriptor import *
from handlers.base_handler import *


class ShowAvailableArchCommand(Command):
    """Shows the available architecture tables for syscalls."""

    @classmethod
    def execute(cls, slack_wrapper, args, channel_id, user_id, user_is_admin):
        """Execute the ShowAvailableArch command."""
        arch_list = SyscallsHandler.syscallInfo.get_available_archs()

        msg = "\n"
        msg += "Available architectures:```"

        for arch in arch_list:
            msg += "{}\t".format(arch)

        msg = msg.strip() + "```"

        slack_wrapper.post_message(channel_id, msg)


class ShowSyscallCommand(Command):
    """Shows information about the requested syscall."""

    @classmethod
    def parse_syscall_info(cls, syscall_entries):
        """Parse syscall information."""
        msg = "```"

        for entry in syscall_entries:
            msg += "{:15} : {}\n".format(entry, syscall_entries[entry])

        return msg.strip() + "```"

    @classmethod
    def execute(cls, slack_wrapper, args, channel_id, user_id, user_is_admin):
        """Execute the ShowSyscall command."""
        arch_obj = SyscallsHandler.syscallInfo.get_arch(args[0].lower())

        if arch_obj:
            # convenience : Try to search syscall by id or by name, depending on what
            # the user has specified
            try:
                syscall_id = int(args[1])
                entry = arch_obj.getEntryByID(syscall_id)
            except:
                entry = arch_obj.get_entry_by_name(args[1].lower())

            if entry:
                slack_wrapper.post_message(channel_id, cls.parse_syscall_info(entry))
            else:
                slack_wrapper.post_message(
                    channel_id, "Specified syscall not found: `{} (Arch: {})`".format(args[1], args[0]))
        else:
            slack_wrapper.post_message(channel_id, "Specified architecture not available: `{}`".format(args[0]))


class SyscallsHandler(BaseHandler):
    """
    Shows information about syscalls for different architectures.

    Commands :
    # Show available architectures
    !syscalls available

    # Show syscall information
    !syscalls show x86 execve
    !syscalls show x86 11
    """

    # Specify the base directory, where the syscall tables are located
    BASEDIR = "addons/syscalls/tables"

    syscallInfo = None

    def __init__(self):
        SyscallsHandler.syscallInfo = SyscallInfo(SyscallsHandler.BASEDIR)

        self.commands = {
            "available": CommandDesc(ShowAvailableArchCommand, "Shows the available syscall architectures", None, None),
            "show": CommandDesc(ShowSyscallCommand, "Show information for a specific syscall",
                                ["arch", "syscall name/syscall id"], None),
        }


handler_factory.register("syscalls", SyscallsHandler())
