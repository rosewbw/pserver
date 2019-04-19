class SkillMapper:
    def __init__(self, skill_data, skill_name_column='skill_name'):
        self.skill_data = skill_data
        self.id_to_serial_dict = skill_data.set_index('skill_id').to_dict()['serial']
        self.serial_to_id_dict = skill_data.set_index('serial').to_dict()['skill_id']
        self.serial_to_name_dict = skill_data.set_index('serial').to_dict()[skill_name_column]
        self.name_to_serial_dict = skill_data.set_index(skill_name_column).to_dict()['serial']

    def id_to_serial(self, id):
        if id in self.id_to_serial_dict.keys():
            return self.id_to_serial_dict[id]
        else:
            return None

    def serial_to_id(self, serial):
        if serial in self.serial_to_id_dict.keys():
            return self.serial_to_id_dict[serial]
        else:
            return None

    def serial_to_name(self, serial):
        if serial in self.serial_to_name_dict.keys():
            return self.serial_to_name_dict[serial]
        else:
            return None

    def name_to_serial(self, name):
        if name in self.name_to_serial_dict.keys():
            return self.name_to_serial_dict[name]
        else:
            return None

