class ScreenTime:
    def __init__(self, tag, date=None):
        if tag is None:
            self.screen = None
            return
        self.date = date
        self.startTime = tag['data-playstarttime']
        self.endTime = tag['data-playendtime']
        self.screen = tag['data-screenkorname']
        self.remainSeats = int(tag['data-seatremaincnt'])
        self.url = "https://www.cgv.co.kr" + tag['href']
        self.IMAX = "IMAX" in self.screen

    def init_with_element(self, item):
        self.date = item.find('PLAY_YMD').text
        self.screen = item.find('SCREEN_NM').text
        self.startTime = item.find('PLAY_START_TM').text
        self.endTime = item.find('PLAY_END_TM').text
        self.remainSeats = int(item.find('SEAT_REMAIN_CNT').text)
        self.IMAX = "IMAX" in self.screen
        self.url = f"http://www.cgv.co.kr/ticket/?MOVIE_CD=20028635&MOVIE_CD_GROUP=20027596&PLAY_YMD={self.date}&THEATER_CD={item.find('THEATER_CD').text}&PLAY_START_TM={self.startTime}&AREA_CD=13&SCREEN_CD={item.find('SCREEN_CD').text}"

    def tuplize(self):
        return (self.screen, self.startTime, self.endTime)

    def __str__(self):
        return f"{self.startTime} - {self.endTime} : {self.screen} ({self.remainSeats}석)\n{self.url}"

    def __eq__(self, other):
        return all([self.startTime == other.startTime, self.endTime == other.endTime, self.screen == other.screen])