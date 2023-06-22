from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.scrollview import MDScrollView
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
import pandas as pd
import math


# Window.size = (450, 800)


class WindowManager(ScreenManager):
    excel_manipulation = ObjectProperty()

    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        self.excel_manipulation = ExcelManipulation()


class Screen2(MDScreen):
    pass


class Screen1(MDScreen):

    '''
    The main screen of the app.  
    
    Creates the dropdown menu for selecting the week
    and day of the workout program (e.g., Week 3, Day 4) which in turn update the
    information in the DataTable.

    Also creates a stopwatch with a start/reset button.  
    (No stop functionality to the button because no one needs that in a fitness app.)
    '''

    week_selection = StringProperty("1")
    day_selection = StringProperty("1")
    stopwatch_time = StringProperty("00:00.00")
    milliseconds = NumericProperty()
    seconds = NumericProperty()
    minutes = NumericProperty()

    def __init__(self, **kwargs):
        super(Screen1, self).__init__(**kwargs)

        self.excel_manipulation = ExcelManipulation()
        self.week_menu = MDDropdownMenu(width_mult=2)
        self.day_menu = MDDropdownMenu(width_mult=2)
        self.populate_week_items()
        self.populate_day_items()

    def populate_week_items(self):
        '''
        Gets the number of weeks (which are found in the excel using the ExcelManipulation class)
        and populates that number of dropdown items into a dropdown menu.
        '''
        num_weeks = self.excel_manipulation.num_weeks
        #creating the menu items
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Week {i}",
                "on_release": lambda x=str(i): self.week_menu_callback(x)
            }
            for i in range(1, num_weeks + 1)
        ]
        #adding the menu items to the week menu
        self.week_menu.items = menu_items

    def populate_day_items(self):
        '''
        Gets the number of days (which are found in the excel using the ExcelManipulation class)
        and populates that number of dropdown items into a dropdown menu.
        '''
        num_days = self.excel_manipulation.num_days
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Day {i}",
                "on_release": lambda x=str(i): self.day_menu_callback(x)
            }
            for i in range(1, num_days + 1)
        ]
        self.day_menu.items = menu_items

    def week_open_menu(self, caller):
        '''Open the week menu when it is pressed.'''
        self.week_menu.caller = caller
        self.week_menu.open()

    def week_menu_callback(self, instance):
        '''
        Update the datatable by calling the update_data_table function when 
        a week menu item is pressed.  Then close the menu.
        '''
        self.week_selection = instance
        self.update_data_table()
        self.week_menu.dismiss()

    def day_open_menu(self, caller):
        '''Open the day menu when it is pressed.'''
        self.day_menu.caller = caller
        self.day_menu.open()

    def day_menu_callback(self, instance):
        '''
        Update the datatable by calling the update_data_table function when 
        a day menu item is pressed.  Then close the menu.
        '''
        self.day_selection = instance
        self.update_data_table()
        self.day_menu.dismiss()

    def update_data_table(self):
        '''Update the DataTable'''
        self.ids.data_table.update_tables(
            self.week_selection,
            self.day_selection
        )

    # Stopwatch functionality:
    def start_reset_stopwatch(self):
        '''Start or reset the stopwatch.'''
        self.stopwatch_time = "00:00.00"
        self.milliseconds = 0
        self.seconds = 0
        self.minutes = 0
        Clock.unschedule(self.get_string_time)
        Clock.schedule_interval(self.get_string_time, 0.1)

    def get_string_time(self, dt):
        '''Get the formatted string representation of the stopwatch time.'''
        self.increment_milliseconds()

        milliseconds = str(self.milliseconds)
        seconds = str(self.seconds)
        minutes = str(self.minutes)

        if len(milliseconds) < 2:
            milliseconds = '0' + milliseconds

        if len(seconds) < 2:
            seconds = '0' + seconds

        if len(minutes) < 2:
            minutes = '0' + minutes

        self.stopwatch_time = minutes + ":" + seconds + "." + milliseconds

    def increment_milliseconds(self):
        '''Increment the milliseconds by 10ms'''
        self.milliseconds += 10

        if self.milliseconds == 100:
            self.increment_seconds()
            self.milliseconds = 0

    def increment_seconds(self):
        '''Increment the seconds by 1 second'''
        self.seconds += 1

        if self.seconds == 60:
            self.increment_minutes()
            self.seconds = 0

    def increment_minutes(self):
        '''Increment the minutes by 1 minute'''
        self.minutes += 1


class ExcelManipulation():

    '''
    Reads in the workout program excel.  Note, the program must be filled into the
    Workout Program Template.xlsx.  Reading the spreadsheet doesn't work if the 
    formatting is not strictly followed.

    ExcelManipulation provides the following information:

    row_data is the default info from Week 1, Day 1 of the program.
    new_row_data is the workout info from the relevant week and day being selected from the dropdown menu.
    num_weeks is the total number of weeks in the workout program.
    num_days is the maximum number of days for any given week.
    '''

    def __init__(self):
        self.df = pd.read_excel("Workout Program Template.xlsx")
        self.num_weeks = self.df['Week'].max()
        self.num_days = self.df['Day'].max()

        self.week = 1
        self.day = 1
        self.data_manipulation()

    def data_manipulation(self):
        '''
        get the relevant week and day workout info and transform it so it 
        can be displayed in the DataTable
        
        returns row_data
        '''
        self.week_info = self.df[(self.df['Week'] == self.week) & (self.df['Day'] == self.day)]

        # add a column to the row data and exclude week and day columns
        set_status = []
        # icon = ("checkbox-blank-outline", [1, 0, 0, 1], "")
        icon = 0
        self.cleaned_df = self.week_info[['Exercise', 'Weight', 'Reps', 'Sets']]
        for i in range(len(self.cleaned_df)):
            set_status.append(icon)
        self.cleaned_df.insert(loc=4, column="status", value=set_status)  # cleaned_df['Status'] = set_status  #

        # Making the rows to be displayed in the MDDataTable
        self.row_data = self.cleaned_df.values.tolist()
        return self.row_data

    def update_weekday(self, week_input, day_input):
        '''
        Updates the week and day information.  Called by pressing dropdown menu items
        '''
        self.week = int(week_input)
        self.day = int(day_input)

        new_row_data = self.data_manipulation()
        return new_row_data


class DataTable(MDScrollView):

    '''
    Creates the DataTable in which the workout program is displayed
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        em = ExcelManipulation()
        self.workout_info = em.data_manipulation()

        # setting the column names and filling in the row info. 
        self.data_tables = MDDataTable(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            rows_num=20,
            background_color_header="#BC6122",
            column_data=[
                ("Exercise", dp(35)),
                ("Weight", dp(12)),
                ("Reps", dp(10)),
                ("Sets", dp(10)),
                ("", dp(10))
            ],
            row_data=self.workout_info
        )

        self.data_tables.bind(on_row_press=self.exercise_status)
        self.add_widget(self.data_tables)

    def update_tables(self, new_week, new_day):
        '''Update the tables when buttons are pressed'''
        em = MDApp.get_running_app().root.excel_manipulation
        new_row_data = em.update_weekday(new_week, new_day)
        self.data_tables.row_data = new_row_data

    def exercise_status(self, instance_table, instance_cell_row):
        '''
        Replacing the pressed row to update workout set status 
        (a counter that counts up to the number of sets for that exercise.)
        Only updates the set counter cells at index 4, 9, 14, 19, etc. 
        '''
        

        row_index = math.floor(instance_cell_row.index / 5)
        old_data = self.data_tables.row_data[row_index]
        num_sets = self.data_tables.row_data[row_index][3]
        set_counter = self.data_tables.row_data[row_index][4]

        if set_counter < num_sets:
            set_counter += 1
            self.data_tables.row_data[row_index][4] = set_counter
            self.data_tables.update_row(old_data, self.data_tables.row_data[row_index])
        elif set_counter >= num_sets:
            set_counter = 0
            self.data_tables.row_data[row_index][4] = set_counter
            self.data_tables.update_row(old_data, self.data_tables.row_data[row_index])
        else:
            pass


class FitnessApp(MDApp):

    '''
    Build the app.  Read in the relevant kv file that (mostly) determines styling.
    '''

    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.theme_style = "Dark"

        return Builder.load_file("fitness.kv")


FitnessApp().run()
