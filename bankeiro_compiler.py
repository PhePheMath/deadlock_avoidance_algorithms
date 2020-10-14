import curses
import re


class system_viewer():

    def show_list(self, stdsrc, iterable, axis_y=1, axis_x=1, column_size=25,
                  commands=False, pointer=-1, title='No Title'):
        title_config = '|{:^'
        title_config += str((
            len(iterable)//column_size)*len(iterable[0])+len(iterable[0])-2)
        title_config += '}|'
        title = title_config.format(title)

        stdsrc.addstr(axis_y-1, axis_x, title)

        for index, string in enumerate(iterable):
            relative_column_position = (index//column_size)*len(string)
            relative_row_position = (index % column_size)
            y = axis_y+relative_row_position
            x = axis_x+relative_column_position

            stdsrc.addstr(y, x, string)
            if commands and index == pointer:
                stdsrc.addstr(y, x, string, curses.A_STANDOUT)
        return x, y


class bankeiro(system_viewer):
    def __init__(self):
        self.allocation = []  # list with allocated resources
        self.max_need = []  # list with what processes need to completion
        self.max_resources = ()  # tuple with the max of each resource

    def get_info(self, text):
        any_string_after_comment_tag = '//.*?\n'

        info = re.sub(any_string_after_comment_tag,  '\n',  text)
        info = info.split('\n')
        self.max_resources = tuple(map(int, info[0].split()))
        self.allocation = [list(
            map(int, process.split())
            ) for process in info[1:(len(info)//2)+1:]]
        self.max_need = [tuple(
            map(int, process.split())
            ) for process in info[(len(info)//2)+1::]]

    def get_allocated(self):
        allocated = [0, ]*len(self.max_resources)
        for process in self.allocation:
            for resource, number_allocations in enumerate(process):
                allocated[resource] += number_allocations

        return allocated

    def get_available(self):
        available = [0, ]*len(self.max_resources)
        allocated = self.get_allocated()
        limit = self.max_resources

        for resource in range(len(self.max_resources)):
            available[resource] = limit[resource] - allocated[resource]

        return available

    def get_remaining_need(self, number_process):
        remaining_need = [0, ]*len(self.max_resources)

        alloc = self.allocation[number_process]
        needs = self.max_need[number_process]

        for resource in range(len(self.max_resources)):
            remaining_need[resource] = needs[resource] - alloc[resource]

        return remaining_need

    def find_adequate_process(self):
        available = self.get_available()
        still_need = self.get_remaining_need

        for index in range(len(self.allocation)):
            for resource in range(len(self.max_resources)):
                if still_need(index)[resource] > available[resource]:
                    break
            else:
                return index

        return -1

    def delete_process(self, number_process):
        self.allocation.pop(number_process)
        self.max_need.pop(number_process)

    def run_banker_s_algorithm(self):
        process = self.find_adequate_process()

        if process > -1:
            curses.wrapper(self.show_progress, process)

        if process > -1:
            self.delete_process(process)
            return True
        elif not len(self.allocation):
            curses.wrapper(self.show_safe_result)
            return False
        else:
            curses.wrapper(self.show_unsafe_result)
            return False

    def show_safe_result(self, stdsrc):
        stdsrc.clear()
        y, x = stdsrc.getmaxyx()
        stdsrc.addstr(y//2, (x//2)-12, 'Safe state Encountered!!!')
        stdsrc.refresh()
        stdsrc.getch()

    def show_unsafe_result(self, stdsrc):
        stdsrc.clear()
        y, x = stdsrc.getmaxyx()
        stdsrc.addstr(y//2, (x//2)-12, 'Safe state Encountered!!!')
        stdsrc.refresh()
        stdsrc.getch()

    def show_progress(self, stdsrc, process):
        stdsrc.clear()
        show_processes = ['|{:^15} {:^15}|'.format(
            str(self.allocation[index]),
            str(self.get_remaining_need(index))
            ) for index in range(len(self.allocation))]

        available = self.get_available()
        max_resources = str(self.max_resources)
        still_need = str(self.get_remaining_need(process))

        self.show_list(
            stdsrc, show_processes,
            3, 45, commands=True,
            pointer=process,
            title='{:^15} {:^15}'.format('Have', 'Need'))

        stdsrc.addstr(3, 3, 'Máximo de recursos: {:^20}'.format(max_resources))
        title_config = f'{"{:^"+str(len(str(available)))+"}"}'
        title_config = f'{title_config} {title_config}'
        stdsrc.addstr(5, 3, title_config.format('Need', 'Available'))
        stdsrc.addstr(6, 3, title_config.format(still_need, str(available)))

        stdsrc.refresh()
        stdsrc.getch()


if __name__ == "__main__":
    text = open('bankeiro_algorithm/allocations').read()
    b = bankeiro()

    b.get_info(text)
    while True:
        if not b.run_banker_s_algorithm():
            break
