#### SIMU PROJECT ####

###Libraries###
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx 
import numpy.random as rng
import pandas as pd
import random
import operator


#### CLASSES ####

#### NETWORK STRUCTURE ####
n = 50
keys=["complex" , "friendly" , "meaning","polish" , "multi", "action", "difficulty", "abstract"]

def getscore(dic1,dic2):
            #used in influencer assignment
    sco=0
    for a in keys:
        sco+=abs(dic1[a]-dic2[a])
    sco=(1-sco/len(keys))
    return sco

#### NETWORK STRUCTURE ####
class Network(object):
    def __init__(self, size=n):
        self.size=size
        self.mean=0
        self.sd=0
        self.watchers=[]
        self.dist=0
        self.type=0
        self.agentsid=[]
        self.agents=[]
        self.inf=[]
        self.gf=nx.Graph()
        #not sure if dgraph is still needed. if just doesnt work, try graph witout di
        self.ginf=nx.Graph()
        self.infperag=1
        self.numinf=10
        self.infdic={}
        self.infobj=[]
        self.pos=0
        
    def generate(self,meanfriends=5, sdfriends=5, frienddist="uni",connectdist="watstro"):
                #generates object and the f network
        for a in range(self.size):
            self.gf.add_node(a,obj=Agent(a))
        if connectdist=="CStyle":
            for a in range(self.size):
                #
                
                #self.gf.add_node(a,obj=______object_____)
                
                #
                tar=["r"]
                friends=[]
                for b in list(self.gf[a]):
                    friends.append(b)
                    for c in list(self.gf[b]):
                        tar.append(c)
                    
                
                if frienddist=="uni":
                    #numf=rng.uniform()
                    #numf=numf*meanfriends//1+5
                    numf=5
                    #numf=15-len(friends)
                    #if numf <0:
                     #   numf=1
                    numf=int(numf)
                if connectdist=="CStyle":
                    for aa in range(numf):
                        nex=rng.choice(tar)
                        if nex=="r" or int(nex) in friends+["r",a]:
                            while nex in friends+["r",a] or int(nex) in friends+["r",a]:
                                nex=int(rng.choice(range(self.size)))
                        nex=int(nex)
                        self.gf.add_edge(a,int(nex))
                        tar=tar+list(self.gf[nex])
                        friends.append(nex)
                if len(self.gf[a])<5:
                    print(a)
                    print(friends)
                    print(self.gf[a])
                    print(" \n")
        elif connectdist=="randomunif":
            #notperfect
            numf=10
            connect={k:[] for k in range(self.size)}
            li=[]
            for a in range(self.size-1):
                it=0
                while len(connect[a])<numf and it<100:
                    it+=1
                    r=rng.choice(range(a+1,self.size))
                    if len(connect[r])<10 or r in connect[a]:
                        #print(a,r)
                        li.append([int(a),int(r)])
                        connect[a].append(r)
                        connect[r].append(a)
                print(a,it,len(connect[a]))
            print(len(li))
            for b,c in li:    
                self.gf.add_edge(b,c)
                #gnm_random_graph(n, m, seed=None, directed=False)
                #connected_watts_strogatz_graph(n, k, p[, ...])
            #if len(self.gf[a])<5:
             #   print(a)
              #  print(friends)
               # print(self.gf[a])
                #print(" \n")
        elif connectdist=="randomunif2":
            al=[]
            numf=10
            for a in range(numf):
                al=al+list(range(self.size))
            con=[]
            al2=al
            rng.shuffle(al2)
            it=0
            while it<10000:
                it+=1
                if len(al2)>=1:
                    cand=al2[:2]
                    if cand[0]!=cand[1] and cand not in con and cand[::-1] not in con:
                        con.append(frozenset(al2[:2]))
                        al2=al2[2:]
                    else:
                        rng.shuffle(al2)
                else:
                    break
            print(con,len(con),len(set(con)),it)
            for b,c in con:    
                self.gf.add_edge(b,c)
        elif connectdist=="prederd":
            n=self.size
            k=10/(n-1)
            te=nx.gnp_random_graph(n,k)
            self.gf.add_edges_from(te.edges)
        elif connectdist=="watstro":
            n=self.size
            p=0.05
            k=10
            te=nx.connected_watts_strogatz_graph(n,k,p,100) 
            self.gf.add_edges_from(te.edges)
        elif connectdist=="bara":
            n=self.size
            p=0.05
            k=5
            te=nx.barabasi_albert_graph(n,k)
            self.gf.add_edges_from(te.edges)
        elif connectdist=="pow":
            n=self.size
            #k=min(n/10,5)
            k=4
            p=0.05
            te=nx.powerlaw_cluster_graph(n,k,p) 
            self.gf.add_edges_from(te.edges)
        elif connectdist=="full":
            n=self.size
            e=[]
            for a in range(n-1):
                for b in range(a+1,n):
                    e.append(set([a,b]))
            self.gf.add_edges_from(e)
                
                
                #karate_club_graph()
        elif connectdist=="star":
            n=self.size
            e=[]
            for a in range(n):
                e.append([a,(n+1)%n])
            self.gf.add_edges_from(e)
        elif connectdist=="circle":
            n=self.size
            e=[]
            for a in range(n):
                e.append([a,(a+1)%n]) 
            self.gf.add_edges_from(e)
                #karate_club_graph()
                
        else:
            raise Exception("ERROR: UNVALID GENERATE KEY")

        self.agentsid=self.gf.nodes
        for a in self.agentsid:
            self.agents.append(self.getobj(a))
            
            friendsinstances = []
            for friend in self.friendsof(a):
                    temp = self.getobj(friend)
                    friendsinstances.append(temp)
            self.getobj(a).define_friends(friendsinstances)
        self.pos = nx.spring_layout(self.gf)

            
            
    def setup(self, genway="random"):
        #sets up tastes and assigns the inf stuff
        pref={}
        for a in keys:
            pref[a]=0
        for a in self.gf.nodes():
            dic=pref
            for b in keys:
                dic[b]=rng.random()
            self.getobj(a).define_preferences(dic)
                
        ninf=5
        
        inf=random.sample(self.gf.nodes,ninf)
        for a in inf:
            self.infobj.append(self.getobj(a))
        watchers=self.agentsid
        for a in range(self.size):
            self.ginf.add_node(a,obj=self.getobj(a))
        infdic={}
        for a in inf:
            infdic[a]=[]
        if genway=="random":
            for a in watchers:
                b=random.choice(inf)
                infdic[b].append(a)
                self.ginf.add_edge(b,a)
        if genway=="stricttaste":
            for a in watchers:
                pref=self.getobj(a).preferences
                sco=-100000000000

                nu=0
                for b in range(ninf):
                    be=inf[b]
                    inpref=self.getobj(be).preferences
                    s=getscore(pref,inpref)
                    if sco<s:
                        nu=b
                        sco=s
                infdic[inf[nu]].append(self.getobj(a)) #attention check
            self.ginf.add_edge(a,inf[nu])
        if genway=="unstricttaste":
            for a in watchers:
                pref=self.getobj(a).preferences
                sco=[]
                for b in range(ninf):
                    be=inf[b]
                    inpref=self.getobj(be).preferences
                    sco.append(getscore(pref,inpref))
                nu=rng.choice(range(ninf),1,sco)
                infdic[inf[nu]].append(a)
            self.ginf.add_edge(a,inf[nu])
        if genway=="double":
            #might not work
            for a in watchers:
                b=random.choice(inf)
                infdic[b].append(a)
                self.ginf.add_edge(b,a)
            for a in watchers:
                pref=self.getobj(a).preferences
                sco=-100000000000
                nu=0
                for b in range(ninf):
                    be=inf[b]
                    inpref=self.getobj(be).preferences
                    s=getscore(pref,inpref)
                    if sco<s:
                        nu=b
                        sco=s
            infdic[inf[nu]].append(a)
            self.ginf.add_edge(a,inf[nu])
            
        #puts the inf stuff into a usable form
       
        self.infdic=infdic
        
        for influencer in self.infdic:
            influencers_total.append(self.getobj(influencer))
            self.inf.append(influencer)
        
        for influencer in self.infdic:
            followerinstances = []
            for follower in infdic[influencer]:     
                temp = self.getobj(follower)
                followerinstances.append(temp)
            
            self.getobj(influencer).define_followers(followerinstances)   
            
#        for a in self.infdic.keys():       #old version
#            self.getobj(a).define_followers(self.infdic[a])
#            for b in self.infdic[a]:
#                self.getobj(b).influencer=self.getobj(a)
                
                
#        self.agentsid=self.gf.nodes
#        for a in self.agentsid:
#            self.agents.append(self.getobj(a))
#            
#            friendsinstances = []
#            for friend in self.friendsof(a):
#                    temp = self.getobj(friend)
#                    friendsinstances.append(temp)
#            self.getobj(a).define_friends(friendsinstances)                


    def friendsof(self,personnr):
        return(list(self.gf[personnr]))
        
    def getobj(self,personnr):
        return self.gf.nodes[personnr]["obj"]
    
    def draw(self):
        ax=plt.gca()
        ax.clear()
        fig = plt.gcf()
        cols=[]
        for a in list(self.gf.nodes):
            cols.append(getnodecol(int(self.getobj(a).now_playing)))     #lets clear this one up later
        fig.set_size_inches(60,60)#    set dimension of window
        nx.draw(self.gf,self.pos, node_size=100,node_color=cols)
        
    def drawi(self):
        ax=plt.gca()
        ax.clear()
        fig = plt.gcf()

        temp=nx.create_empty_copy(self.gf)
        temp.add_edges_from(self.ginf.edges)
        cols=[]
        for a in list(self.gf.nodes):
            cols.append(getnodecol(self.getobj(a).now_playing.game_id))
        nx.draw(temp, node_colors=cols)
    def addinf(self):
                ####sketch, can be erased
        #choose numinf randomagents as infs
        # generate score for each inf according to taste similarity
        # chose infperag ones according to score
        pass
        #probably output a dic of ags per inf, but also add inf as a trait of ag
    def niceplot(self):
        ax=plt.gca()
        ax.clear()
        fig = plt.gcf()
        fig.set_size_inches(30,30)
        toplot=nx.Graph()
        #print(self.inf)
        for a in self.agents:
            if a.node_num in self.inf:
                eee="s"
                #print(a.now_playing)
                aaa=3500#+10*a.played_games[a.now_playing]#update time playing with self.played_games[self.now_playing]
            else:
                eee="^"
                #print(a.now_playing)
                aaa=1500#+5*a.played_games[a.now_playing]
            toplot.add_node(a.node_num,col=getnodecol(int(a.now_playing)),size=aaa,shape=eee)
            
        toplot.add_edges_from(self.gf.edges,col="k",wei=2)
        #for aa in range(len(self.inf)):
         #   a=self.inf[aa]
          #  for b in list(self.ginf[a]):
           #     toplot.add_edge(a,b,col=getcol(aa),wei=5)
        toplot.add_edges_from(self.ginf.edges,col="r",wei=1)
        
        edges=toplot.edges
        nodes=toplot.nodes
        #print(self.inf)
        colors = [toplot[u][v]['col'] for u,v in edges]
        wei = [toplot[u][v]['wei'] for u,v in edges]
        coln=[toplot.nodes[u]["col"] for u in nodes]
        size=[toplot.nodes[u]["size"] for u in nodes]
        #print(size)
        print([nodes[x] for x in self.inf])
         #shape=[toplot.nodes[u]["shape"] for u in nodes]
        #print(colors)
        nx.draw_networkx(toplot, self.pos, nodes=nodes, node_color= coln, node_size=size, 
                #node_shape="d",
                with_labels=False,
                edges=edges, edge_color=colors, 
                width=wei
                )
        #nx.draw_networkx_nodes(toplot, self.pos, nodes=[nodes[x] for x in self.inf], node_color=[coln[x] for x in self.inf], node_size=2500, 
         #       node_shape="d",
          #      with_labels=False,
                #edges=edges, edge_color=colors, 
                #width=wei
           #     )
def getcol(a):
    col=["g","b","y","m","r"]
    return col[a]
def getnodecol(id):
    trans=["k","r","b","y","m","g","olive","lightpink"]
    #apply list to transltate ids into python colours here
    id=trans[id]
    return id
#### AGENTS ####
people_total = [] #list of person objects
influencers_total = []
games_total = [] #list of game objects
games_dict = {0:0} #dictionary of str(game objects)
friendship_prob = 0.2
influencer_prob = 0.15
advertising_power = 0.1
standard_decay = -0.15
decay_multiplier =0.2
comparison_budget = 0.5

likes = ['singleplayer', 'multiplayer', 'casual', 'replayable', 'rpg']
genres = ['fps', 'puzzle', 'strategy', 'platformer', 'sim']


class Agent:      
    def __init__(self,node_num):
        self.node_num = node_num          #ID of agent
        self.friends = []
        self.played_games = {} #key:name of game, value:nr of times played
        self.followers = []
        self.influencer = 0
        self.knowngames = {}
        self.preferences = {}
        self.preferences_list=[]
        self.now_playing = "0"       #player initialized as playing the "0" game, the NUll game dummy
        self.time_playing = 0
        self.influencer_status = False
        people_total.append(self)
        for game in games_total:
            self.knowngames[game.name]= 0           #fills up the preference list of the agent with all the known games
        
    def __str__(self):
        return self.node_num

    def define_friends(self, friends_list):
        self.friends = friends_list
        
    def define_followers(self, followers_list):
        self.followers.extend(followers_list)
        self.influencer_status = True
        
#    def define_knowngames(self, games_dict):
#        self.knowngames = games_dict.copy()
    
#    def set_preferences(self,likes:list):
#        self.preferences_list=likes
        

    def define_preferences(self, pref_dict ={}):
        self.preferences = pref_dict
        #else:
         #   if scores:
          #      for i in range(len(scores)):
           #         self.preferences[self.preferences_list[i]]=scores[i]
            #for item in self.preferences_list:
             #   if item not in self.preferences:
              #      self.preferences[item]= 0
        
    def get_friends(self):
        return self.friends
    
    def get_followers(self):
        return self.followers
    
    def get_knowngames(self):
        return self.knowngames
    
    def get_preferences(self):
        return self.preferences
    
    def influence_playing(self,key,prob,bo=0):       #key is the knowngame name
        if key!= "0":
            #print("game with name:" + key)
            newprob = self.knowngames[key]
            if bo==1:
                newprob+=prob
            else:
                newprob += prob*getscore(games_total[int(key)].scores,self.preferences)
            self.knowngames[key] = newprob
            #print(self.knowngames)
    
    def decay_playing(self):
        self.knowngames[self.now_playing] += standard_decay
    
    def recommend(self):
        for friend in self.friends:
            friend.influence_playing(self.now_playing,friendship_prob)
        if self.followers:

            for follower in self.followers:
                follower.influence_playing(self.now_playing,influencer_prob)
            

    def game_infection(self):
        
        #print (self.knowngames)
        temp = self.knowngames.copy()          #copy of the known games dictionary
        del temp["0"]           #exclude the Null game from the temp dictionary
#        print (temp)
        while temp:         #as long as the temporary dictionary is non empty
            dictval = max(temp, key=temp.get) #finds the highest key
#            if dictval in self.played_games:            #do not want to play twice the same game
#                del temp[dictval]
#                continue
            if random.random() < temp[dictval]:
                self.now_playing = dictval      #dictval is the name of the played game
                if dictval in self.played_games:     #if already played, add of 1 the value
                    temp = self.played_games[dictval]
                    temp += 1
                    self.played_games[dictval] = temp
#                if self.played_games and dictval not in self.played_games:
                else:     
                    self.played_games[self.now_playing] = 0         #initializes the game with 1 timestamp played
                break
            else:
                del temp[dictval]   #erases the highest value item from the temporary dict
       # print (self.knowngames)
            
    def decay_effect(self):
        if self.now_playing != "0":
            disinterest =self.played_games[self.now_playing]**2*standard_decay       #a bit hardcoded, does not look for the decay value of the single game, rather uses the standard decay directly!!
            self.influence_playing(self.now_playing, disinterest,bo=1)

  
class Game:

    game_num = 0
    
    def __init__(self, budget, name = game_num, game_id = game_num, decay = 0, genre = 0, scores = {}):
        self.name = str(Game.game_num)
        self.budget = budget
        self.decay = standard_decay
        self.genre = genre
        self.scores = scores
        self.effect = advertising_power*self.budget/comparison_budget
        self.game_id = game_id
        games_total.append(self)
        games_dict[str(self)]=0
        Game.game_num += 1
        
    def __str__(self):
        return str(self.name)
        
    def get_popularity(self, people=people_total):
        players = 0
        for i in people:
            if self.name == i.now_playing:
                players += 1
        self.popularity = players/len(people)
        return self.popularity
    
    def get_totalplayers(self, people=people_total):
        players = 0
        for i in people:
            if self.name == i.now_playing:
                players += 1
        return players
    
    def run_add(self, people=people_total):
        print(self.name)
        for person in people:
            person.influence_playing(self.name, self.effect)
    

    def define_scores(self, keys=likes, scores_list=[], scores_dic={}):
        if scores_dic:
            self.scores = scores_dic
        elif scores_list:
            for i in range(len(scores_list)):
                self.scores[keys[i]]=scores_list[i]
        for item in keys:
            if item not in self.scores:
                self.scores[item] = 0
    
#    def find_agent_from_agent_ID(self, agentID):
#        for agent in people_total:
#            if agent
    

#    def set_decay(self, value=standard_decay):
#        self.decay = value


    
    
#### CONVERSION ALGORITHM ####
    
class Conversionalgo:
    def __init__(self, step_num=0):
        self.counter = step_num
        self.currentstatus = {}
        
    # def implement_influence(self):        #commented out because now in simumanager
    #     for item in games_total:
    #         item.run_add()
    #     for person in people_total:
    #         person.recommend()              #ev in game class
    #     for person in people_total:
    #         person.game_infection()
    
    def get_currentstatus(self):
        for item in games_total:
            self.currentstatus[str(item)] = item.get_totalplayers()
        
    def get_deltas(self):
        pass
    #more?

#### SIMULATION MANAGER ####

timestamp = 0

class Simumanager:
    'class that manages the simulation & works with timestamps'

    def __init__(self):
        global timestamp 
        timestamp = 0            #init the timestamp to 0 for a new simulation

#    def loadsimu(self, timestamp, datafile):
#        timestamp = timestamp

    def addgames(self,gamesnumber=5, budget="random"):  #create n instances of games, which automatically get added in games_total list
        pref={}
        for a in keys:
            pref[a]=0
         
        if budget == "random":
            budgetamount = random.random()
            for i in range(0,gamesnumber):
                
                dic=pref
                for b in keys:
                    dic[b]=rng.random()
                Game(budgetamount,scores=dic)
        else:                                           #open for extension for non random assignment of budget
            raise Exception("ERROR: INVALID BUDGET PARAMETER INPUT")

    def networkinit(self,agentsnumber=500,influassignment="random"):      #creates n agents (500 as preset), assigns preferences,
        net = Network(size=agentsnumber)
        net.generate()   # using watstro simulation as preset
        net.setup(influassignment)  #random, stricttaste, unstricttaste, double keys for influencer init and assignment

    def drawnetwork(self,type="agents"):
        if type == "agents":
            self.net.draw()
        if type == "influencers":
            self.net.drawi()
        if type == "agents_influencers":
            self.net.niceplot()
        else:
            raise Exception("Error: INVALID TYPE PARAMETER INPUT")

    def stateofknowngame(self):     #1 Timestamp
        pass
    
    def adround(self):
        print("adround")
        for game in games_total:
           # print(game.name)
            if game.name !="0":         #there wont be an AD for a Non Game
#                runadd = input("Ad for game " + str(game.name) + "? \n give a nonempty input to run an add          ")
                runadd = 1
                if runadd:
                    game.run_add()


    def influfriendround(self):
        print("influencer & friends effect")
        for person in people_total:
            person.recommend()          #includes friend influence over other friends, and influencers influence

    def conversion(self):               #decides which game gets played
        print("conversion")
        for person in people_total:
            person.game_infection()

    def exporttimestamp(self):
        pass

    def get_agents(self):
        pass

    def get_games(self):
        pass

    def decay(self):
        print("decay")
        for person in people_total:
            person.decay_effect()

    def nextstep(self):             #increases timestamp of simulation by 1
        global timestamp 
        timestamp += 1

##### DATA MANAGER ####

class Datamanager:          #call it after the network creation, to instantiate a pandas matrix that has the information
                            #about all the agents at timestamp = 0
    def __init__(self):
        self.columns = ["timestamp", "agent ID", "isinfluencer", "current played game", "how long been playing current game", "# friends playing the same", "does influencer play the same"]
        
        if games_total:                 #appends to the index list the names of the played games list
            for game in games_total:
                if game.name != "0":
                    self.columns.append("game " + str(game.name) + " preference %")     
        self.listofagents = []
        self.table = pd.DataFrame(data = self.listofagents, columns = self.columns)

    def get_table(self):
        print (self.table)

    def update_table(self):
        print("update")
        for person in people_total:
            agent = []
            agent.append(timestamp)             #timestamp of simulation
            agent.append(person.node_num)       #id
            agent.append(int(person.influencer_status))     #1 if influencer
            agent.append(person.now_playing)
            if person.now_playing != "0":
                agent.append(person.played_games[person.now_playing])       # how long been playing 
            else: agent.append(0)
            amount = 0
            for friend in person.friends:
                if friend.now_playing == person.now_playing:
                    amount += 1
            agent.append(amount) #nr friends playing the same game
            
            isalsoplaying = 0
            for influencer in influencers_total:
                if person in influencer.followers:
                    if person.now_playing == influencer.now_playing:  
                        isalsoplaying = 1                       
            agent.append(isalsoplaying) #is influ playing the same?
            
            for game in games_total:        
                if game.name != "0":
                    agent.append(person.knowngames[game.name])
                    #agent.append("placeholder")
            self.listofagents.append(agent)
            
        self.table = pd.DataFrame(data = self.listofagents, columns = self.columns)
            
    def export_table(self):
        writer = pd.ExcelWriter('Simulation.xlsx', engine='xlsxwriter')
        self.table.to_excel(writer, sheet_name='Sim')
        writer.save()
        
    def createtable(self):
        pass
    def savecurrenttimestamp(self):
        pass


#sim = Simumanager()
#sim.addgames()
#sim.networkinit()
#sim.drawnetwork()
#data = Datamanager()
#data.get_table()
#data.export_table()
       
        
def main(): 
    print ("START OF SIMULATION \n")
    sim = Simumanager()
    sim.addgames(8)
    net = Network()
    net.generate()
    net.setup()
    data = Datamanager()

    #print ("Table:\n \n")
    #data.get_table()
    rounds = int(input("How many rounds of simulation?      "))
    for i in range(rounds):
        global timestamp
        print("Timestamp " + str(timestamp))
        

        if i == 0:       
            sim.adround()               #influence of ads, influencers and friends & conversion calculated
        sim.influfriendround()
        sim.conversion()
        
        data.update_table()         #export values in the table

        #data.get_table()
        data.export_table()
        
        sim.decay()
        
        
        net.niceplot()                  #draw plot
        pic=plt.gcf()
        pic.savefig(str(timestamp)+".png")
        
        
        if i < (rounds-1):
#            input("Proceed with next step?: ")
            timestamp += 1
        else:
            print("Simulation finished.")
        
    
if __name__ == "__main__":
    main()

##### PLOTTER ####
#        
#class plotter:
#    def setupplot():
#        pass
#    def drawnodes():
#        pass
#    def drawedges(node, depth):     #node: person & influencer, depth: how many levels of friends of friends of frieds i.e.
#        pass
#    def update():
#        pass
#    def exportplot():
#        pass