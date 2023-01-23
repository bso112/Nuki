import pytchat
import datetime
import os
from datetime import datetime, timedelta, timezone
from os.path import exists

from youtubeAPI import fetchStartTime


def parseChatTime(time: str) -> datetime:
    return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')


def parseUTC(time: str) -> datetime:
    return datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')


def to_str(delta: timedelta) -> str:
    form = '%02d'
    return f"{form % (delta.seconds // 3600)}:{form % (delta.seconds // 60 % 60)}:{form % (delta.seconds % 60)}"


def isMatchWithKeyword(word: str):
    for keyword in ["yabe", "lol", "lewd"]:
        if word.lower().__contains__(keyword):
            return True
    return False


CLIP_LENGTH = 60

if __name__ == '__main__':
    clipCount = int(input("input count of clip you want\n"))
    videoId = input("input video id\n")
    videoFilePath = input("input video file path\n")

    if not exists(videoFilePath):
        print("file not exist")
        exit(0)

    chat = pytchat.create(video_id=videoId)
    actualStartTime = parseUTC(fetchStartTime(videoId))
    gradeList = []

    print("analyzing...")
    maxGrade = 0
    totalChatCnt = 0
    while chat.is_alive():
        items = chat.get().items
        totalChatCnt += len(items)
        if not items:
            continue

        chatTime = parseChatTime(items[0].datetime) - timedelta(hours=9)
        if chatTime < actualStartTime:
            continue

        grade = sum(1 for item in items if isMatchWithKeyword(item.message))
        if maxGrade < grade:
            maxGrade = grade
        gradeList.append((chatTime - actualStartTime, grade))

    highlights = sorted(gradeList, key=lambda x: x[1], reverse=True)[:clipCount]

    print(f"highlights {highlights}\n")
    print(f'max grade: {maxGrade}\ntotal chat count: {totalChatCnt}')

    for index, highlight in enumerate(highlights):
        highlightTime = highlight[0]
        clipStartTime = to_str(highlightTime - timedelta(seconds=CLIP_LENGTH // 2))
        clipEndTime = to_str(highlightTime + timedelta(seconds=CLIP_LENGTH // 2))

        print(clipStartTime, clipEndTime)

        outputFilePath = f'{videoFilePath}_output_{index}.mp4'
        os.system(
            f"ffmpeg -i {videoFilePath} -ss {clipStartTime} -to {clipEndTime} -c:v copy -c:a copy {outputFilePath}")
