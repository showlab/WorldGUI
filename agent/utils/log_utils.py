def state_updater(before_msg):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.update_state({"in_progress": True, "current_progress": before_msg})
            result = func(self, *args, **kwargs)
            if before_msg.endswith("..."):
                after_msg = before_msg.replace("...", "Finished")
            else:
                after_msg = before_msg + " Finished"
            self.update_state({"in_progress": False, "current_progress": after_msg})
            return result
        return wrapper
    return decorator