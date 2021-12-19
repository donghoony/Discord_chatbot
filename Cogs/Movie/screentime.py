class ScreenTime:
    def __init__(self, tag):
        if tag is None:
            self.screen = None
            return
        self.startTime = tag['data-playstarttime']
        self.endTime = tag['data-playendtime']
        self.screen = tag['data-screenkorname']
        self.remainSeats = tag['data-seatremaincnt']
        self.url = "https://www.cgv.co.kr" + tag['href']
        self.IMAX = "IMAX" in self.screen

    def init_with_element(self, item):
        self.screen = item.find('SCREEN_NM').text
        self.startTime = item.find('PLAY_START_TM').text
        self.endTime = item.find('PLAY_END_TM').text
        self.remainSeats = int(item.find('SEAT_REMAIN_CNT').text)
        self.IMAX = "IMAX" in self.screen
        self.url = None

    def __str__(self):
        return f"{self.startTime} - {self.endTime} : {self.screen} ({self.remainSeats}석)\n{self.url}"