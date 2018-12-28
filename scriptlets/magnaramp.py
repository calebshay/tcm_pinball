from mpf.core.custom_code import CustomCode

class Magnaramp(CustomCode):

    def on_load(self):
        self.info_log('Enabling')
        self.magnaramp_in_progress = False
        self.auto_fire = self.machine.get_machine_var('magnaramp_auto_fire')

        #if self.machine.switch_controller.is_active('s_jump_ball_vuk'):
            #self.upkick_to_magnet()

        self.machine.events.add_handler('ball_started', self.enable)
        self.machine.events.add_handler('ball_ended', self.disable)

    def enable(self, **kwargs):
        del kwargs

        self.info_log('Enabling')

        if self.auto_fire:
            self.add_vuk_handler()

        self.machine.events.add_handler(
            'magnaramp_vuk_firing', self.enable_magnet)
        self.machine.events.add_handler(
            'magnaramp_magnet_disabled', self.choose_lane)

    def disable(self, **kwargs):
        del kwargs

        self.info_log('Disabling')

        self.remove_vuk_handler()
        self.machine.events.remove_handler_by_event(
            'magnaramp_vuk_firing', self.enable_magnet)
        self.machine.events.remove_handler_by_event(
            'magnaramp_magnet_disabled', self.choose_lane)

        self.disable_magnet()

    def remove_vuk_handler(self):
        self.info_log('Remove handler')
        self.machine.switch_controller.remove_switch_handler(
            's_jump_ball_vuk', self.fire_vuk, 1, 500)

    def add_vuk_handler(self, **kwargs):
        self.info_log('Add handler')
        self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.fire_vuk, 1, 500)

    def suspend_vuk_handler(self):
        self.remove_vuk_handler()
        self.delay.add(3000, self.add_vuk_handler)

    def fire_vuk(self, **kwargs):
        del kwargs

        self.suspend_vuk_handler()
        self.machine.events.post('magnaramp_vuk_firing')
        self.machine.coils['c_jump_ball_vuk'].pulse()

    def disable_magnet(self, **kwargs):
        del kwargs

        self.info_log('magnet disabled')
        self.machine.coils['c_jump_ball_magnet'].disable()
        self.machine.events.post('magnaramp_magnet_disabled')

    def choose_lane(self, **kwargs):
        del kwargs

        if self.machine.get_machine_var('magnaramp_left'):
            self.ramp_left()
        else:
            self.ramp_right()

        self.toggle_direction()

    def enable_magnet(self, **kwargs):
        del kwargs

        self.info_log('magnet enabled')
        self.machine.coils['c_jump_ball_magnet'].enable()
        self.delay.add(500, self.disable_magnet)

    def toggle_direction(self):
        self.machine.set_machine_var(
            'magnaramp_left', not self.machine.get_machine_var('magnaramp_left'))

    def ramp_left(self):
        self.info_log('ramp_left')
        self.machine.coils['c_jump_ball_right_kicker'].pulse()

    def ramp_right(self):
        self.info_log('ramp_right')
        self.machine.coils['c_jump_ball_top_kicker'].pulse()
