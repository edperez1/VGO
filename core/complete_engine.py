import sys

class CompleteEngine:
    def __init__(self):
        # Catálogo completo con todas las variantes incluyendo el formato completo de las ONUs
        self.commands = [
            "show version", "show running-config", "show startup-config", "show run interface gpon-olt_1/1/1","show clock",
            "show card", "show run interface gpon-onu_1/1/8:4","show subrack", "show power", "show fan", "show temperature",
            "show process", "show memory", "show cpu", "show ip-route", "show interface",
            "show vlan", "show mac-address-table", "show ont", "show tcont", "show gemport",
            "show service-port", "show users", "show security", "show log",
            "show card status", "show system-ip", "show flash", "show boot-time",
            "show interface brief", "show interface description", "show interface transceiver",
            "show interface olt-optical-info", "show ont info", "show ont optical-info",
            "show ont capability", "show ont version", "show ont run-state", "show ont distance",
            "show ont mac-address", "show ont alarm", "show vlan summary", "show dba-profile",
            "show traffic", "show qos-profile", "show privilege", "show ntp", "show snmp",
            "show dhcp-snooping", "show storm-control", "show gpon onu distance",
            "show gpon onu detail-info", "show gpon remote-onu interface video",
            "show gpon onu uncfg", "show gpon onu unconfigured", "show gpon onu state",
            "show pon power attenuation", "show gpon remote-onu capability", "show gpon onu by sn",
            "show system-group", "show processor", "show onu-type gpon", "show tcp brief",
            "show card-temperature", "show card slotno 2", "show card slotno 3",
            "show card slotno 4", "show gpon remote-onu ip-host", "show gpon remote-onu model",
            "show gpon remote-onu equip", "show gpon remote-onu interface eth",
            "show gpon remote-onu interface wifi", "show run int", "show gpon profile traffic",
            "show gpon onu state gpon-olt_1/1/1",
            "show gpon onu detail-info gpon-onu_1/1/1:1",
            "show gpon onu detail-info gpon-onu_1/1/8:5",
            "show gpon onu distance gpon-onu_1/1/1:1",
            "show pon power attenuation gpon-onu_1/1/1:1",
            "show pon power attenuation gpon-onu_1/1/8:65",
            "show gpon remote-onu capability gpon-onu_1/1/1:1",
            "show gpon remote-onu interface video gpon-onu_1/1/1:1",
            "show gpon remote-onu ip-host gpon-onu_1/2/1:3",
            "show gpon remote-onu model gpon-onu_1/2/2:17",
            "show gpon remote-onu equip gpon-onu_1/2/2:17",
            "show gpon remote-onu interface eth gpon-onu_1/2/2:17",
            "show gpon remote-onu interface wifi gpon-onu_1/2/2:17",
            "show mac gpon onu gpon-onu_1/2/3:18",
            "show run int gpon-onu_1/4/1:2",
            "show int optical-module-info xgei_1/21/1",
            "configure terminal", "configure vlan", "configure interface", "configure dba-profile",
            "interface gpon-olt", "interface gei", "interface xgei", "interface loopback",
            "interface brief", "interface description", "ont confirm", "ont delete", "ont modify",
            "tcont profile", "gemport tcont", "gemport name", "vlan name",
            "service-port multi-service", "username password", "pon onu-type", "write memory",
            "reboot", "reset-card", "swap"
        ]
        
        self.history = []
        self.history_index = -1

    def get_progressive_options(self, current_input):
        current_input = current_input.lower().strip()
        if not current_input:
            return ""

        matches = [c for c in self.commands if c.startswith(current_input)]
        if matches:
            return matches[0]

        return current_input

    def add_to_history(self, command):
        command = command.strip()
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)

    def get_previous_command(self):
        if not self.history:
            return ""
        if self.history_index > 0:
            self.history_index -= 1
        return self.history[self.history_index]

    def get_next_command(self):
        if not self.history:
            return ""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            return self.history[self.history_index]
        else:
            self.history_index = len(self.history)
            return ""