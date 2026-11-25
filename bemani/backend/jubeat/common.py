import time

from bemani.backend.jubeat.base import JubeatBase
from bemani.protocol import Node


class JubeatLoggerReportHandler(JubeatBase):
    def handle_logger_report_request(self, request: Node) -> Node:
        # Handle this by returning nothing, game doesn't care
        root = Node.void("logger")
        return root


class JubeatDemodataGetNewsHandler(JubeatBase):
    def handle_demodata_get_news_request(self, request: Node) -> Node:
        demodata = Node.void("demodata")
        data = Node.void("data")
        demodata.add_child(data)

        officialnews = Node.void("officialnews")
        data.add_child(officialnews)
        officialnews.set_attribute("count", "0")

        return demodata


class JubeatDemodataGetHitchartHandler(JubeatBase):
    def handle_demodata_get_hitchart_request(self, request: Node) -> Node:
        demodata = Node.void("demodata")
        data = Node.void("data")
        demodata.add_child(data)

        # Not sure what this is, maybe date?
        data.add_child(Node.string("update", time.strftime("%d/%m/%Y")))

        # No idea which songs are licensed or regular, so only return hit chart
        # for all songs on regular mode.
        hitchart_lic = Node.void("hitchart_lic")
        data.add_child(hitchart_lic)
        hitchart_lic.set_attribute("count", "0")

        songs = self.data.local.music.get_hit_chart(self.game, self.music_version, 10)
        hitchart_org = Node.void("hitchart_org")
        data.add_child(hitchart_org)
        hitchart_org.set_attribute("count", str(len(songs)))
        rank = 1
        for song in songs:
            rankdata = Node.void("rankdata")
            hitchart_org.add_child(rankdata)
            rankdata.add_child(Node.s32("music_id", song[0]))
            rankdata.add_child(Node.s16("rank", rank))
            rankdata.add_child(Node.s16("prev", rank))
            rank = rank + 1

        return demodata


class JubeatLobbyCheckHandler(JubeatBase):
    def handle_lobby_check_request(self, request: Node) -> Node:
        root = Node.void("lobby")
        data = Node.void("data")
        root.add_child(data)

        data.add_child(Node.s16("interval", 0))
        data.add_child(Node.s16("entry_timeout", 0))
        entrant_nr = Node.u32("entrant_nr", 0)
        entrant_nr.set_attribute("time", "0")
        data.add_child(entrant_nr)

        return root

    def handle_lobby_entry_request(self, request: Node) -> Node:
        # There is only one cab on this network, so there is never another
        # player to find. Tell the cab that it is the master of room 1.
        # The cab then calls lobby/refresh, and that reply tells it to start.
        #
        # The cab needs all four values below. If one is missing, the cab
        # sends lobby/entry again and the search screen stays for about 22 s.
        # To go back to the old behavior, return Node.void("lobby") here.
        root = Node.void("lobby")
        data = Node.void("data")
        root.add_child(data)

        roomid = Node.s64("roomid", 1)
        roomid.set_attribute("master", "1")
        data.add_child(roomid)

        # Seconds between lobby/refresh calls. 1 is the shortest wait.
        data.add_child(Node.s16("refresh_intr", 1))

        # Send back the song that the cab selected.
        music = Node.void("music")
        data.add_child(music)
        music.add_child(Node.u32("id", request.child_value("data/music/id") or 0))
        music.add_child(Node.u8("seq", request.child_value("data/music/seq") or 0))

        return root

    def handle_lobby_refresh_request(self, request: Node) -> Node:
        # The cab calls this while it waits in a room. "start" = True tells
        # the cab to stop the search and start the song with the players
        # that it has (only itself on this network).
        root = Node.void("lobby")
        data = Node.void("data")
        root.add_child(data)

        data.add_child(Node.s16("refresh_intr", 1))
        data.add_child(Node.bool("start", True))

        return root

    def handle_lobby_report_request(self, request: Node) -> Node:
        # The cab reports who is in the room. The cab reads "refresh_intr"
        # from this reply. If it is missing, the cab sends the report 4 times
        # (about 7 s). To go back, return Node.void("lobby") here.
        root = Node.void("lobby")
        data = Node.void("data")
        root.add_child(data)

        data.add_child(Node.s16("refresh_intr", 1))

        return root


class JubeatGamendRegisterHandler(JubeatBase):
    def handle_gameend_regist_request(self, request: Node) -> Node:
        data = request.child("data")
        player = data.child("player")

        if player is not None:
            refid = player.child_value("refid")
        else:
            refid = None

        if refid is not None:
            userid = self.data.remote.user.from_refid(self.game, self.version, refid)
        else:
            userid = None

        if userid is not None:
            oldprofile = self.get_profile(userid)
            newprofile = self.unformat_profile(userid, request, oldprofile)
        else:
            newprofile = None

        if userid is not None and newprofile is not None:
            self.put_profile(userid, newprofile)

        gameend = Node.void("gameend")
        data = Node.void("data")
        gameend.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.s32("session_id", 1))
        player.add_child(Node.s32("end_final_session_id", 1))
        return gameend


class JubeatGametopGetMeetingHandler(JubeatBase):
    def handle_gametop_get_meeting_request(self, request: Node) -> Node:
        gametop = Node.void("gametop")
        data = Node.void("data")
        gametop.add_child(data)
        meeting = Node.void("meeting")
        data.add_child(meeting)
        single = Node.void("single")
        meeting.add_child(single)
        single.set_attribute("count", "0")
        tag = Node.void("tag")
        meeting.add_child(tag)
        tag.set_attribute("count", "0")
        reward = Node.void("reward")
        data.add_child(reward)
        reward.add_child(Node.s32("total", -1))
        reward.add_child(Node.s32("point", -1))
        return gametop
