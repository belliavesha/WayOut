if True: # import and init
    from numpy import zeros,sqrt,sin,cos,array,sum,prod,dtype
    from random import choice, shuffle, randrange
    import pygame 
    # import gtk
    # res = (gtk.gdk.screen_width(), gtk.gdk.screen_height())
    from pygame.locals import *
    pygame.init()

if True: # colors
    WHITE=(255,255,255)
    BLACK=(0,0,0)
    RED=(255,0,0)
    GREEN=(0,255,0)
    BLUE=(0,0,255)
    floorColor=(0,0,50)
    ceilingColor = (20,20,0)
    thickColor = (250,250,50)
    wallColor = (40,80,0)
    passiveColor = (0, 100, 200)
    activeColor = (200, 50, 50)
    aimColor = (200, 150, 250)
    onceColor = (40,0,0)
    twiceColor = (80,0,0)

if True: # fonts
    sizeOption = 40
    sizeCaption = 60
    sizeText = 20
    fontOption = pygame.font.SysFont("freemono",sizeOption)
    fontCaption = pygame.font.SysFont("comicsansms",sizeCaption)
    fontText = pygame.font.SysFont("monospace", sizeText)

if True: 
    RIGHT = 1
    FORWARD = 2
    UPWARDS = 4
    FASTER = 8 




def floor(x):
    return int(x//1)

def sign(x):
    return 1 if x>0 else -1


class Screen:
    def __init__(self,name,size='default',background=BLACK):
        self.background=background
        if size == 'default' :
            infoObject = pygame.display.Info()
            size = (int(infoObject.current_h*0.9), int(infoObject.current_h*0.9))
        self.display_width=size[0] 
        self.display_height=size[1]
        self.size=size
        self.display=pygame.display.set_mode(size)
        pygame.display.set_caption(name)



class Element:

    def __init__(self):
        self.state = 0
    def show(self,screen):
        pass
    def handle(self,event):
        pass


class Content(Element): 
    def __init__(self,elements):
        self.elements= elements

    def show(self,screen):
        for element in self.elements:
            element.show(screen)
    
    def handle(self, event):
        for element in self.elements:
            value = element.handle(event)
            if value :
                return value 


class Menu(Content): 
    handleContent=Content.handle
    def __init__(self,elements):
        Content.__init__(self, elements)

    def handle(self, event):
        l=len(self.elements)
        if event.type==KEYDOWN and l:
            d={K_DOWN:1,K_UP:-1}
            if event.key in d:
                for e in range(l):
                    if self.elements[e].state:
                        self.elements[e].state=False
                        self.elements[(e+d[event.key])%l].state=True
                        break 
                else:
                    self.elements[0].state=True
        return self.handleContent(event)


class TextBox(Element):
    """TextBox"""
    def __init__(self,center,font,text,color=WHITE):
        self.text = text
        self.font = font
        self.color = color
        self.center=center
        self.surface = font.render(text, 1, color)
        rect = self.surface.get_rect()
        rect.center=center
        self.rect=rect

    def show(self,screen):
        self.surface = self.font.render(self.text, 1, self.color)
        rect = self.surface.get_rect()
        rect.center=self.center
        self.rect=rect
        screen.display.blit(self.surface, self.rect)   
    
class Button(TextBox):
    showTextBox=TextBox.show
    def __init__(self,action,center,font,text,color=WHITE,K_BUTTON=None):
        TextBox.__init__(self,center,font,text,color)
        self.center=center
        self.action=action
        self.K_BUTTON=K_BUTTON
        self.state = 0 

    def show(self,screen):
        self.showTextBox(screen)
        if self.state : 
            pygame.draw.polygon(screen.display, self.color, [
                self.rect.topleft,
                (self.rect.left-self.rect.height/2,self.rect.centery),
                self.rect.bottomleft], 0)
            pygame.draw.polygon(screen.display, self.color, [
                self.rect.topright,
                (self.rect.right+self.rect.height/2,self.rect.centery),
                self.rect.bottomright], 0)

    def handle(self, event):
        if event.type==MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.state=True
            else:
                self.state=False
        if event.type==MOUSEBUTTONDOWN:
            if event.button == 1 and self.state:
                return self.action
        if event.type==KEYDOWN:
            if (event.key == K_RETURN and self.state) or (event.key == self.K_BUTTON):
                return self.action
        return None

class Parameter:
    def __init__(self,name,span=['OFF','ON'],cur=0):
        self.name=name
        self.span=span
        self.cur=cur
        self.last=len(span)-1
        self.value=span[self.cur]

    def next(self):
        self.cur=self.cur+1 if self.cur<self.last else 0
        # min(self.cur+1,self.last)
        self.value=self.span[self.cur]

    def prev(self):
        self.cur=self.cur-1 if self.cur>0 else self.last
        # self.cur=max(self.cur-1,0)
        self.value=self.span[self.cur]
    def __str__(self):
        return str(self.value)

class Option(Button):
    handleButton=Button.handle
    def __init__(self,parameter,center,font,color=WHITE):
        self.parameter=parameter
        Button.__init__(self,self.parameter.next,center,font,str(self),color)

    def handle(self, event):
        self.handleButton(event)
        if self.state:
            self.text=str(self)
        if event.type==KEYDOWN:
            if event.key == K_LEFT and self.state:
                self.parameter.prev()
                self.text=str(self)
            if event.key == K_RIGHT and self.state:
                self.parameter.next()
                self.text=str(self)
    
    def __str__(self):
        return self.parameter.name+": "+str(self.parameter.value)



class Map(Element):
    wallThickness = 0.2
    eps = 1e-5

    # def tpl(self,v):
    #     if self.cell=='tesseract':
    #         return tuple(v)
    #     else: 
    #         x,y,z,t = tuple(v)
    #         t//=2
    #         return (x,y,z,t)    

    def isInside(self,v):
        x,y,z,t = tuple(v)
        if self.cell!='tesseract' and not (x%2==y%2==z%2==t%2):

            return False
        return x>=0 and x<self.Width  and y>=0 and y<self.Height and z>=0 and z<self.Depth and t>=0 and t<self.Fourth

    def delWall(self,v,vn,s):
        if s%2:
            self.walls[tuple(vn)] += (2**(s//2))
        else:
            self.walls[tuple(v)] += (2**(s//2))


    def __init__(self, Width = 5, Height = 5, Depth = 5, Fourth = 5, cell = 'tesseract', mazetype = 'labyrinth', vis = None, extra = 0.0 ):
        self.mazetype = mazetype
        self.Width = Width
        self.Height = Height
        self.Depth = Depth
        self.Fourth = Fourth
        self.cell = cell

        self.vis = vis

        self.dims = array([Width, Height, Depth, Fourth],dtype = int)
        self.size = prod(self.dims)

        # self.pos = array([0,0,Depth-1,Fourth-1],dtype = int)
        self.pos = array([0,0,0,0],dtype = int)
        
        self.exit = array([Width-1,Height-1,0,0],dtype = int)
        
        self.walls = zeros(self.dims,dtype = int)
        
        visited = zeros(self.dims,dtype = int) 
        self.visited =  zeros(self.dims,dtype = int)





        if cell == 'tesseract':
            self.dcs = [
                array([0+1,0,0,0],dtype=int), array([0-1,0,0,0],dtype=int),
                array([0,0+1,0,0],dtype=int), array([0,0-1,0,0],dtype=int),
                array([0,0,0+1,0],dtype=int), array([0,0,0-1,0],dtype=int),
                array([0,0,0,0+1],dtype=int), array([0,0,0,0-1],dtype=int)] 

            self.ssd = [(0,1),(0,2),(3,2),(3,1)]

        else:

            # self.dcs = [
            #     array([+1,+1,-1,-1],dtype=int), array([-1,-1,+1,+1],dtype=int),
            #     array([+1,-1,+1,-1],dtype=int), array([-1,+1,-1,+1],dtype=int),
            #     array([+1,-1,-1,+1],dtype=int), array([-1,+1,+1,-1],dtype=int),
            #     array([+1,+1,+1,+1],dtype=int), array([-1,-1,-1,-1],dtype=int),
            #     array([+1,+1,+1,-1],dtype=int), array([-1,-1,-1,+1],dtype=int),
            #     array([+1,+1,-1,+1],dtype=int), array([-1,-1,+1,-1],dtype=int),
            #     array([+1,-1,+1,+1],dtype=int), array([-1,+1,-1,-1],dtype=int),
            #     array([-1,+1,+1,+1],dtype=int), array([+1,-1,-1,-1],dtype=int)]
            self.dcs = [
                array([0+2,0,0,0],dtype=int), array([0-2,0,0,0],dtype=int),
                array([0,0+2,0,0],dtype=int), array([0,0-2,0,0],dtype=int),
                array([0,0,0+2,0],dtype=int), array([0,0,0-2,0],dtype=int),
                array([0,0,0,0+2],dtype=int), array([0,0,0,0-2],dtype=int),
                array([-1,+1,+1,+1],dtype=int), array([+1,-1,-1,-1],dtype=int),
                array([+1,-1,+1,+1],dtype=int), array([-1,+1,-1,-1],dtype=int),
                array([+1,+1,-1,+1],dtype=int), array([-1,-1,+1,-1],dtype=int),
                array([+1,+1,+1,-1],dtype=int), array([-1,-1,-1,+1],dtype=int),
                ] 
            self.ssd = [(0,1),(2,3),(4,5),(6,7)]

        self.dcl = len(self.dcs)

        if mazetype == 'depth-first':
            first = array([choice(range(Width)),choice(range(Height)),choice(range(Depth)),choice(range(Fourth))],dtype=int)
            while self.cell!='tesseract' and not self.isInside(first):
                first = array([choice(range(Width)),choice(range(Height)),choice(range(Depth)),choice(range(Fourth))],dtype=int)
            print(first)
            path = [first]

            while path:
                nexts = []
                v = path[-1] 
                visited[tuple(v)] = 1
                for s in range(self.dcl):
                    vn = v+self.dcs[s]
                    if self.isInside(vn) and visited[tuple(vn)]<0.5: nexts.append((vn,s,))
                if nexts:
                    vn, s = choice(nexts)
                    self.delWall(v,vn,s)
                    path.append(vn)
                else: path.pop()

        elif mazetype == 'breadth-first':

            first = array([choice(range(Width)),choice(range(Height)),choice(range(Depth)),choice(range(Fourth))],dtype=int)
            while self.cell!='tesseract' and not self.isInside(first):
                first = array([choice(range(Width)),choice(range(Height)),choice(range(Depth)),choice(range(Fourth))],dtype=int)
            print(first)
            path = [(first,-1)]
            # self.visited[tuple(first)]=2
            while path:
                v,s = path.pop(randrange(0,len(path)))
                vn = v - self.dcs[s] 
                if visited[tuple(v)]<0.5:
                    if s>=0: 
                        self.delWall(vn,v,s)
                    for s in range(self.dcl):
                        vn = v+self.dcs[s]
                        if self.isInside(vn) and visited[tuple(vn)]<0.5: path.append( (vn,s,) )
                visited[tuple(v)] = 1

        elif mazetype == 'random-walks':
            doors = zeros(self.dims,dtype = int) 
            verts = [array([i,j,k,l],dtype = int) for i in range(Width) for j in range(Height) for k in range(Depth) for l in range(Fourth)]

            first = verts.pop()
            visited[tuple(first)] = -1 
            cur = 0

            while verts:

                v = verts.pop() 
                if self.isInside(v):
                    doors[tuple(v)] = -1
                    cur +=1 
                    while visited[tuple(v)]>-0.5:
                        visited[tuple(v)] = cur
                        s =  randrange(0,self.dcl)
                        vn = v-self.dcs[s]
                        if self.isInside(vn):
                            v = vn
                            if visited[tuple(v)]<cur:
                                doors[tuple(v)]=s

                    while doors[tuple(v)]>-0.5:
                        s = doors[tuple(v)]
                        vn = v+self.dcs[s]
                        self.delWall(v,vn,s)
                        v = vn
                        visited[tuple(v)] = -1 




        elif mazetype == 'random-walls' :
            doors = [(array([i,j,k,l],dtype = int),d) for i in range(Width) for j in range(Height) for k in range(Depth) for l in range(Fourth) for d in range(self.dcl//2)]
            shuffle(doors)
            rooms = [[]]
            for v1,d in doors:
                # print(visited)
                if self.isInside(v1):
                    v2 = v1+self.dcs[d*2]
                    if self.isInside(v2):
                        self.walls[tuple(v1)]+=2**d
                        vis1, vis2 = visited[tuple(v1)], visited[tuple(v2)]
                        if vis1>vis2 :
                            v1,vis1,v2,vis2 = v2,vis2,v1,vis1
                        if vis1==0 :
                            if vis2==vis1: 
                                visited[tuple(v1)]=len(rooms)
                                visited[tuple(v2)]=len(rooms)
                                rooms.append([v1,v2])
                            else: 
                                rooms[vis2].append(v1)
                                visited[tuple(v1)] = vis2
                        else:
                            if vis2==vis1 :
                                self.walls[tuple(v1)]-=2**d
                            else:
                                for v2 in rooms[vis2]:
                                    visited[tuple(v2)] = vis1
                                    rooms[vis1].append(v2) 
        else:
            extra = 3.0

        if extra>0.0:
            print(extra,mazetype)
            doors = [(array([i,j,k,l],dtype = int),d) for i in range(Width) for j in range(Height) for k in range(Depth) for l in range(Fourth) for d in range(self.dcl//2)]
            shuffle(doors)
            count = int(extra*(self.size*3-sum(self.size/self.dims))  )
            while count and doors:
                v1,d = doors.pop()
                v =  v1+self.dcs[d*2]
                dw = 2**d
                if self.isInside(v) and not self.walls[tuple(v1)]&dw:
                    self.walls[tuple(v1)]+=dw
                    count -=1
            print(len(doors))

        

    def handle(self,event):
        if event.type==KEYDOWN:
            if event.key == K_ESCAPE:
                return 'menu'
            if event.key == K_p:
                return 'pause'    
            x,y,z,t = self.pos 
            sk = [
                [K_d,K_s,K_a,K_w],
                [K_v,K_c,K_x,K_f],
                [K_m,K_n,K_b,K_h],
                [K_l,K_k,K_j,K_i],]
            for ss in range(4):
                kr,kd,kl,ku = sk[ss]
                d1,d2 = self.ssd[ss]
                if event.key == kr and self.walls[tuple(self.pos)]&2**d1:
                    self.pos += self.dcs[d1*2]
                if event.key == kd and self.walls[tuple(self.pos)]&2**d2:
                    self.pos += self.dcs[d2*2]
                if event.key == kl:
                    self.pos -= self.dcs[d1*2]
                    if not self.isInside(self.pos) or not self.walls[tuple(self.pos)]&2**d1:
                        self.pos += self.dcs[d1*2]
                if event.key == ku:
                    self.pos -= self.dcs[d2*2]
                    if not self.isInside(self.pos) or not self.walls[tuple(self.pos)]&2**d2:
                        self.pos += self.dcs[d2*2]


            if self.vis == 'auto' or (self.vis == 'space' and event.key == K_SPACE): 
                x,y,z,t = self.pos 
                self.visited[x,y,z,t] += 1


        if (self.pos == self.exit).all():
            return 'win'

        return None



    def show(self,screen):
        v = self.pos
        eWidth = 4
        eHeight = 4
        Width = 4*eWidth+2 #self.Width+self.Fourth
        Height = 4*eHeight+2 #self.Height+self.Depth
        # dx =  min(screen.display_width//Width,(8*screen.display_height)//(9*Height))
        # dy =  (9*dx)//8
        dx = screen.display_width//Width
        dy = screen.display_height//Height
        ddx = dx//2
        ddy = dy//2

        wallwidth = 3
        cc = [(eWidth,eHeight),(eWidth,1+3*eHeight),(1+3*eWidth,1+3*eHeight),(1+3*eWidth,eHeight)]
        pygame.draw.polygon(screen.display, floorColor, [(0,0),(0,dy*Height),(dx*Width,dy*Height),(dx*Width,0)],0)
            
        if 'true':
            for i in range(eWidth,-eWidth-1,-1):
                for j in range(eHeight,-eHeight-1,-1):
                    for ss in range(4):
                        d1,d2=self.ssd[ss]
                        vn = v + self.dcs[d1*2]*i + self.dcs[2*d2]*j
                        ew,eh = cc[ss]
                        if self.isInside(vn):
                            color = floorColor
                            if self.vis != "none" :
                                if self.visited[tuple(vn)]>1.5:
                                    color=twiceColor
                                elif self.visited[tuple(vn)]>.5:
                                    color=onceColor
                        else:
                            color = wallColor                        
                        pygame.draw.polygon(screen.display, color, [
                            (dx*(ew+i),dy*(eh+j)),
                            (dx*(ew+i),dy*(eh+j+1)),
                            (dx*(ew+i+1),dy*(eh+j+1)),
                            (dx*(ew+i+1),dy*(eh+j))],0)

                        if self.isInside(vn):
                            if not self.walls[tuple(vn)]&(2**d1):
                                pygame.draw.line(screen.display, wallColor, (1+dx*(ew+i+1),1+dy*(eh+j+1)),(1+dx*(ew+i+1),1+dy*(eh+j)),wallwidth)
                            if not self.walls[tuple(vn)]&2**d2:
                                pygame.draw.line(screen.display, wallColor, (1+dx*(ew+i+1),1+dy*(eh+j+1)),(1+dx*(ew+i),1+dy*(eh+j+1)),wallwidth)
                        pygame.draw.polygon(screen.display, activeColor,[ 
                            ( 1 + dx*ew, 1 + dy*eh+ddy),
                            ( 1 + dx*ew+ddx, 1 + dy*eh+dy),
                            ( 1 + dx*ew+dx, 1 + dy*eh+ddy),
                            ( 1 + dx*ew+ddx, 1 + dy*eh)
                        ]  )
                                



        

        if True and "Draw borders":
            pygame.draw.line(screen.display, thickColor, (dx*Width+wallwidth,dy*Height),(0,dy*Height),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (dx*Width,dy*Height+wallwidth),(dx*Width,0),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (dx*2*eWidth+dx,0),(dx*2*eWidth+dx,dy*Height),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (0,dy*2*eHeight+dy),(dx*Width,dy*2*eHeight+dy),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (0,0),(0,dy*Height),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (0,0),(dx*Width,0),wallwidth*2)


        if False and "draw aim":
            pygame.draw.polygon(screen.display, aimColor,[ 
                ( 1 + dx*(self.Width )-ddx, 1 + dy*(self.Height)),
                ( 1 + dx*(self.Width ), 1 + dy*(self.Height) +ddy),
                ( 1 + dx*(self.Width )+ddx, 1 + dy*(self.Height) ),
                ( 1 + dx*(self.Width ), 1 + dy*(self.Height) -ddy)
            ]  )


            

class Main(Element):

    def __init__(self,screen):
        wc=screen.display_width/2
        hc=screen.display_height/2
        self.screen = screen 

        if "Parameters": 
            self.width = Parameter('1st',range(1,26),7)
            self.height = Parameter('2nd',range(1,26),7)
            self.depth = Parameter('3rd',range(1,26),7)
            self.fourth = Parameter('4th',range(1,26),7)

            self.cycles = Parameter('% extra ways',[0.,.1,1.,10,50,99])
            self.vis = Parameter('Paint',['auto','space','none'],cur =1)

            self.cell = Parameter('Cell',['tesseract','orthoplex'])

            self.shape = Parameter('Build',['breadth-first','depth-first','random-walls','random-walks','empty'],cur = 2)

        if "Contents":
            self.menuContent=Content([
                    Menu([Button("play",(wc, hc-sizeOption),fontOption,"PLAY",K_BUTTON=K_p),
                        Button("opts",(wc, hc),fontOption,"OPTIONS",K_BUTTON=K_o),
                        Button("info",(wc, hc+sizeOption),fontOption,"INFO",K_BUTTON=K_i),                
                        Button("close",(wc, hc+2*sizeOption),fontOption,"QUIT",K_BUTTON=K_ESCAPE)]),
                    TextBox((wc, hc-2*sizeCaption),fontCaption,"Menu")])

            self.optionsContent = Content([
                        Menu([
                            Button("dims",(wc, hc-sizeOption),fontOption,"DIMENSIONS",K_BUTTON=K_d),
                            Option(self.vis,(wc,hc),fontOption),
                            Option(self.cycles,(wc,hc+sizeOption),fontOption),
                            Option(self.shape,(wc, hc+2*sizeOption),fontOption),
                            Option(self.cell,(wc, hc+3*sizeOption),fontOption),
                        Button("menu",(wc, hc+4*sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
                        TextBox((wc, hc-2*sizeCaption),fontCaption,"Options")])

            self.mapContent = Content([
                    Menu([
                        Option(self.width,(wc,hc-sizeOption),fontOption),
                        Option(self.height,(wc,hc),fontOption),
                        Option(self.depth,(wc,hc+sizeOption),fontOption),
                        Option(self.fourth,(wc, hc+2*sizeOption),fontOption),
                        Button("opts",(wc, hc+3*sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
                    TextBox((wc, hc-2*sizeCaption),fontCaption,"DIMENSIONS")])

            self.winContent = Content([
                    Menu([Button("cont",(wc, hc-sizeOption),fontOption,"CONTINUE",K_BUTTON=K_c),
                        Button("play",(wc, hc),fontOption,"NEW GAME",K_BUTTON=K_p),
                        Button("menu",(wc, hc+sizeOption),fontOption,"MENU",K_BUTTON=K_m),                
                        Button("close",(wc, hc+2*sizeOption),fontOption,"QUIT",K_BUTTON=K_ESCAPE)]),
                    TextBox((wc, hc-2*sizeCaption),fontCaption,"Well done!")])

            self.pauseContent = Content([
                    Menu([Button("cont",(wc, hc-sizeOption),fontOption,"CONTINUE",K_BUTTON=K_c),
                        Button("play",(wc, hc),fontOption,"NEW GAME",K_BUTTON=K_p),
                        Button("menu",(wc, hc+sizeOption),fontOption,"MENU",K_BUTTON=K_m),                
                        Button("close",(wc, hc+2*sizeOption),fontOption,"QUIT",K_BUTTON=K_ESCAPE)]),
                    TextBox((wc, hc-2*sizeCaption),fontCaption,"Paused")])

            self.infoContent=Content([
                        TextBox((wc, hc-7*sizeText),fontText,"This is a four-dimensional reach-the-end game. "),
                        TextBox((wc, hc-6*sizeText),fontText,"The algorithm can build either a maze or a labyrinth-like route"),
                        TextBox((wc, hc-5*sizeText),fontText,"After that some of the walls can be removed."),
                        TextBox((wc, hc-4*sizeText),fontText,"Four maps show the projections onto the plane of two coordinates."),
                        TextBox((wc, hc-3*sizeText),fontText,"The red tiles are movable with WASD and IJKL keys respectively. "),
                        TextBox((wc, hc-2*sizeText),fontText,"And the blue tiles are just for convenience."),
                        TextBox((wc, hc-1*sizeText),fontText,"The aim is to move from one corner of the maze to the opposit one"),
                        TextBox((wc, hc-0*sizeText),fontText,"then all the tiles meet in the center of the screen."),
                        TextBox((wc, hc+1*sizeText),fontText,"The player can also paint the floor of the room he is in."),
                        TextBox((wc, hc+2*sizeText),fontText,"Good luck with this shit!"),
                        Menu([Button("menu",(wc, hc+2*sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
                    ])

        self.content = self.menuContent
        self.currentMap = None
        self.play()
    
    def pause(self):
        self.stopped=True

    def fill(self,content):
        self.content=content

    def update(self):
        self.screen.display.fill(self.screen.background)
        self.content.show(self.screen)
        pygame.display.update()
        

    def show(self,screen):
        self.content.show(screen)

    def handle(self,event):
        value = self.content.handle(event)
        if value == 'close' or event.type == QUIT :
            pygame.quit()
            quit()
        if value == 'play':
            self.content = Map(
                self.width.value,
                self.height.value,
                self.depth.value,
                self.fourth.value,
                self.cell.value,
                self.shape.value,
                self.vis.value,
                self.cycles.value/100.)
        if value == 'opts':
            self.content = self.optionsContent
        if value == 'dims':
            self.content = self.mapContent
        if value == 'menu' :
            self.content = self.menuContent
        if  value == "win":
            self.currentMap = self.content
            self.currentMap.exit =  -1
            self.content  =  self.winContent
        if  value == "cont":
            self.content = self.currentMap 
        if  value == "pause":
            self.currentMap = self.content
            self.content  =  self.pauseContent
        if  value == "info":
            self.content  =  self.infoContent

            
    def play(self):
        while True:
            for event in pygame.event.get():
                self.handle(event)
            self.update()
            pygame.time.delay(100) 




Main(Screen('M4ZE'))

