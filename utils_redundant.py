import math

"""
This python library contains functions that can be performed
more efficiently by other functions within supported libraries


"""

# datetime.datetime(year, month,day).strftime("%A")
# datetime.date(year, month, day).strftime("%A")
def autocalendar(input_date):
    """
    Takes datetime.datetime or datetime.date input and returns
    the day of the week and if the year is a leap year as a dict.

    this script utilizes the following formula:
	w = { d + floor(2.6*m-0.2) + y + floor(y/4) + floor(c/4)-2*c} mod 7
    a Disparate Variation of Gauss's Algorithm to calculate the day of the week

    d := date of the month
    m := adjusted month number: 
        January = 11, February = 12, March = 1, April = 2, ..., December = 10
    c := last 2 digits of a 4 digit year
    y := first 2 digits of a 4 digit year
        if m == 11 || m == 12
        y = y - 1
    w := day of week: Sunday = 0, Monday = 1, ..., Sunday = 6

    Sources:
    https://repl.it/languages/python3
    https://en.wikipedia.org/wiki/Determination_of_the_day_of_the_week
    used Disparate variation under Gauss's Algorithm 
    https://en.wikipedia.org/wiki/Leap_year#Algorithm
    """

    day_list = [
        'Sunday', 'Monday', 'Tuesday', 'Wednesday', 
        'Thursday', 'Friday', 'Saturday'
    ]
    month_list = [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    month = input_date.month
    date = input_date.day
    year = input_date.year

    # calculation of c and y from a numberical year utilizing a string
    if year >= 1000:
        year_string = str(year)
    elif year <= 999 and year >= 100:
        year_string = '0'+'0'+str(year)
    elif year <= 99 and year >= 10:
        year_string = '0'+'0'+str(year)
    elif year <= 9:
        year_string = '0'+'0'+'0'+str(year)
    c = int(year_string[0])*10 + int(year_string[1])
    y = int(year_string[2])*10 + int(year_string[3])


    # modification of y for January and February
    if month == 1 or month == 2:
        y = y - 1

    # calculation of d from date of month
    d = date

    # calculation of m from month of year (shifting the month number)
    m = month - 2
    if month == 11 or month == 12:
        m += 12

    # calculation of day of the week
    #w = (d + math.floor(2.6*m-0.2) + y + math.floor(y/4) + math.floor(c/4)-2*c) % 7
    w = (d + math.floor(2.6*m-0.2) + y + y//4 + c//4-2*c) % 7
    print(
        day_list[int(w)] + ", " + month_list[month-1] + ", " 
        + str(date) + ", " + str(year)
    )

    # calculation of leap year
    if year % 4 != 0:
        print(str(year) + " is not a leap year.")
        leap_year = False
    elif year % 100 != 0:
        print(str(year) + " is a leap year.")
        leap_year = True
    elif year % 400 != 0:
        print(str(year) + " is not a leap year.")
        leap_year = False
    else:
        print(str(year) + " is a leap year")
        leap_year = True
    return {'day':day_list[w], 'leap_year':leap_year}

# np.stort(ar)
def bubble_sort(the_list):
    """
    Takes an input list and uses the bubble sort algorithm to return a sorted list
    Function will print each of the iterative steps to show its work.
    """
    if_sorted = 0 # -1 if the list is sorted, a whole number if sorting still needs to occur
    y = 0 # number of iterations.  Using name 'y' to for consistancy with version 1

    print(y, ") ", the_list)
    # loop only runs if the list is not completely sorted
    while if_sorted >= 0:
        # compare an element in the list with the element that follows it.  
        # Swap the two elements if necessary
        for x in range (0, len(the_list) - 1 ):
            if the_list[x] > the_list[x + 1]:
                placeholder = the_list[x]
                the_list[x] = the_list[x + 1]
                the_list[x + 1] = placeholder
                if_sorted += 1
                y += 1
                print(y, ") ", the_list)
            x += 1

        # Check if any sorting occurred. Reset if_sorted counter appropriately.
        if if_sorted > 0:
            if_sorted = 0
        else:
            if_sorted = -1

    return the_list