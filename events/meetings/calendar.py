"""
from random import randint
def last_rooms(Last_room: list, time: list, room: int) -> list:
    if time[1] > Last_room[2]:
        Last_room[0] = Last_room[2]
        Last_room[1] = Last_room[3]
        Last_room[2] = time[1]
        Last_room[3] = str(room + 1)
    elif time[1] == Last_room[2]:
        Last_room[3] += str(room + 1)
    elif time[1] > Last_room[0]:
        Last_room[2] = time[1]
        Last_room[3] = str(room + 1)
    return Last_room


def partition(numbers: list) -> list:
    if len(numbers) <= 1:
        return numbers
    else:
        x = randint(0, len(numbers) - 1)
        point = numbers[x][0]
        right_list = []
        left_list = []
        element_list = []

        for i in range(len(numbers)):
            if numbers[i][0] > point:
                right_list.append(numbers[i])
            elif numbers[i][0] == point:
                element_list.append(numbers[i])
            else:
                left_list.append(numbers[i])

        return partition(left_list) + element_list + partition(right_list)


def rooms_list(list_rooms: list, number_room: int = -1):
    n = len(list_rooms)
    rooms_lists = {i + 1: partition(list_rooms[i]) for i in range(n)}
    if number_room > 0:
        return rooms_lists[number_room]
    else:
        return rooms_lists



K = int(input()) # колличество комнат (1)
N = int(input()) # колличество сотрудников, желающих забронить

s = 0
List_room = []
Last_room = [0, "0", 0, "0"]
K_list = [[] * K for i in range(K)]

for i in range(N):
    time = list(map(int, input().split()))

    for j in range(K):
        if len(K_list[j]) == 0:
            s += 1
            Last_room = last_rooms(Last_room, time, j)
            K_list[j].append(time)
            List_room.append(j + 1)
            break
        else:
            marker = True
            for m in range(len(K_list[j])):
                if (time[0] in range(K_list[j][m][0], K_list[j][m][1] + 1)
                        or time[1] in range(K_list[j][m][0], K_list[j][m][1] + 1)
                        or K_list[j][m][0] in range(time[0], time[1] + 1)
                        or K_list[j][m][1] in range(time[0], time[1] + 1)):
                    marker = False
                    break
            if marker and time[0] >= 0 and time[1] <= 600:
                Last_room = last_rooms(Last_room, time, j)
                s += 1
                K_list[j].append(time)
                List_room.append(j + 1)
                break
            #elif j == K - 1:
                #print("Мест нет")

print(f"{s} {List_room[-2]}")


print(f"Расписание всех комнат:{rooms_list(K_list)}")

print(f"Расписание для 1 комнаты:")
first_room = rooms_list(K_list, 1)
for i in range(len(first_room)):
    print(f'{first_room[i]}')

print(Last_room)
"""
import datetime
from models import Place


def calendar(id_place: int, event_date: datetime.date,
             start_time: datetime.time, end_time: datetime.time) -> dict[str: [tuple[str]]]:  # 1 2024-02-15T15:13

    event_time = (start_time, end_time)
    timetable = dict(Place.objects.get(id=id_place)['timetable'])
    if timetable is None:
        timetable = {event_date: [event_time]}
    elif timetable[event_date] is None:
        timetable[event_date] = event_time
    else:
        for i in range(len(timetable[event_date])):
            if end_time < timetable[event_date][i][0] or start_time > timetable[event_date][i][1]:
                timetable[event_date].add(event_time)
    return timetable

    # print(id_place)
    # timetable = Place.objects.get(id=id_place)['timetable']
    # if timetable == '':
    #    timetable = {}
