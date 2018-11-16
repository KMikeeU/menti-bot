import requests
import json
import time
import _thread

class MentiException(Exception):
	pass

class Menti():
	def __init__(self, gameid: str, verify=True, proxies = None):
		self.gameid = gameid
		self.proxies = proxies
		self.verify = verify

		self.base = "https://www.menti.com"
		self.core_conn = "/core/objects/vote_ids/"
		self.keys_conn = "/core/objects/vote_keys/"

		self.recent = {}
	
	def update(self):
		# -- GETTING BASE DATA
		game_req = requests.get(self.base+self.core_conn+self.gameid, proxies=self.proxies, verify=self.verify)
		self.recent = game_req.json()
		return game_req.json()

	def parse(cq: dict):
		if cq["type"] == "choices":
			def run():
				qp = [str(i["label"]) + ": " + str(i["id"]) for i in cq["choices"]]
				print("\n".join(qp))
				ans = input("Your choice: ")
				return ans
		elif cq["type"] == "open":
			def run():
				ans = input("Your answer: ")
				return ans
		elif cq["type"] == "choices_images":
			def run():
				qp = [str(i["label"]) + ": " + str(int(i["id"]) - int(cq["choices"][0]["id"]) + 1) for i in cq["choices"]]
				print("\n".join(qp))
				ans = input("Your choice: ")
				return str(int(ans) + int(cq["choices"][0]["id"]) - 1)
		else:
			def run():
				print(cq)
				input("This type of question (" + cq["type"] + ") ist not supported yet!")
				return ""
		return run

class MentiClient():
	def __init__(self, mentiutils: Menti, verify=True, proxies = None):
		self.utils = mentiutils
		self.proxies = proxies
		self.verify = verify

		self.base = "https://www.menti.com"
		self.identifier_conn = "/core/identifier"
		self.id_conn = "/core/objects/vote_ids/"
		self.keys_conn = "/core/objects/vote_keys/"
		self.vote_conn = "/core/vote"

	def identify(self):
		identifier_headers = {
			"Accept": "application/json",
			"Referer": "https://www.menti.com/"+self.utils.gameid,
			"Content-type": "application/json; charset=UTF-8",
		}

		try:
			identifier_req = requests.post(self.base+self.identifier_conn, headers=identifier_headers, data={}, proxies=self.proxies, verify=self.verify)
			self.identifier = identifier_req.json()["identifier"]
			return self.identifier
		except:
			raise MentiException("Error getting identifier.")

	def default_vote(self, qi: str, qt: str, qans: str):
		requests.post(self.base+self.vote_conn, headers={"Cookie":"identifier1="+self.identifier, "X-Identifier":self.identifier}, json={"question":qi, "question_type":qt,"vote":qans}, proxies=self.proxies, verify=self.verify)
		return True

class MentiBot():
	def __init__(self, menti: Menti, bots: list):
		self.bots = bots
		self.menti = menti
	
	def identify(self):
		print("Identifying " + str(len(self.bots)) + " bots and buffering for response! (CTRL+C to stop buffer)")
		try:
			for bot in self.bots:
				_thread.start_new_thread(bot.identify, ())
			time.sleep(5)
		except KeyboardInterrupt:
			print("Canceling buffer, this may break things!")

	def loop(self):
		while True:
			self.menti.update()
			qid = self.menti.recent["pace"]["active"]
			#print(qid)

			for c,q in enumerate(self.menti.recent["questions"]):
				if q["id"] == qid:
					cq = self.menti.recent["questions"][c]
					break

			vk = cq["vote_key"]

			print(cq["question"])
			try:
				ans = Menti.parse(cq)()
			except KeyboardInterrupt:
				break
			except Exception:
				continue
			if ans == "":
				continue
			self.vote(vk, cq["type"], ans)

	def vote(self, qi: str, qt: str, qans: str):
		for bot in self.bots:
			_thread.start_new_thread(bot.default_vote, (qi, qt, qans))

# proxies = {
# 	"http": "127.0.0.1:8080",
# 	"https": "127.0.0.1:8080"
# }

# verify = False

mentid = input("Menti ID: ")

menti = Menti(mentid)

am = int(input("Amount of Bots (1 Thread per bot): "))

bots = [MentiClient(menti) for i in range(am)]

bot = MentiBot(menti, bots)
bot.identify()
bot.loop()