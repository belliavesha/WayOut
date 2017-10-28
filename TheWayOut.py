if True: # import and init
    from time import sleep
    from random import random as rnd
    from random import shuffle 
    import pygame 
    from pygame.locals import *
    pygame.init()

if True: # object codess and constants
    EMPTY=0
    EXIT=1
    ZEROSPEED=30
    WINDOW='TheWayOut'
    ENEMYMOVE=USEREVENT + 1

if True: # colors
    WHITE=(255,255,255)
    BLACK=(0,0,0)
    RED=(255,0,0)
    lineColor=(200,0,0)
    playerColor=(234,0,40)
    wallColor=(245,245,0)
    floorColor=[(0,0,0),(0,20,0),(0,40,0),(0,80,0)]
    exitColor=(255,90,0)
    playerColors=[(0,240,0),(0,0,200),(0,240,200)]
    enemyColor=(200,0,0)

if True: # directions
    further = lambda i, j, d, s: { 
        6: {
            0: (i ,j-1),    
            1: (i-1,j-1),
            2: (i-1 ,j),
            3: (i,j+1),
            4: (i+1 ,j+1),
            5: (i+1 ,j)
            },
        4: {
            0: (i ,j-1),    
            1: (i-1 ,j),
            2: (i,j+1),
            3: (i+1 ,j)
            }
        }[s][d%s]

    controlkeys=[
    [K_a,K_q,K_w,K_e,K_d,K_s],
    [K_j,K_u,K_i,K_o,K_l,K_k],
    [K_KP4,K_KP7,K_KP8,K_KP9,K_KP6,K_KP5],
    ]

if True: # fonts
    sizeOption = 40
    sizeCaption = 60
    sizeText=20
    fontOption = pygame.font.SysFont("freemono",sizeOption)
    fontCaption = pygame.font.SysFont("comicsansms",sizeCaption)
    fontText = pygame.font.SysFont("monospace", sizeText)

class Screen:
    def __init__(self,name,size=(600,600),background=BLACK):
        self.display_width=size[0] 
        self.display_height=size[1]
        self.size=size
        self.background=background
        self.display=pygame.display.set_mode(size)
        pygame.display.set_caption(name)

mainScreen=Screen(WINDOW,(600,692)) #812

class Element:
    screen=mainScreen
    state=0
    def show(self):
        pass
    def handle(self,event):
        pass
    def move(self):
        pass

class Content(Element): 
    def __init__(self,elements):
        self.elements= elements

    def show(self):
        for element in self.elements:
            element.show()
    
    def handle(self, event):
        for element in self.elements:
            element.handle(event)

    def move(self):
        for element in self.elements:
            element.move()

class Menu(Content): 
    def __init__(self,elements):
        Content.__init__(self, elements)

    def handle(self, event):
        for element in self.elements:
            element.handle(event)
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

class Game(Element):
    def __init__(self):
        self.speed=ZEROSPEED
        self.stopped=False

    def pause(self):
        self.stopped=True

    def fill(self,content):
        self.content=content

    def show(self):
        self.screen.display.fill(self.screen.background)
        self.content.show()
        pygame.display.update()

    def handle(self,event):
        if event.type == QUIT : close()
        self.content.handle(event)

    def move(self):
        if not self.stopped:
            self.content.move()
            pygame.time.delay(int(1.25**(ZEROSPEED-self.speed))) 

    def play(self):
        while True:
            self.move()
            for event in pygame.event.get():
                self.handle(event)
            self.show()

game=Game() # the main global object

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

    def show(self):
        self.surface = self.font.render(self.text, 1, self.color)
        rect = self.surface.get_rect()
        rect.center=self.center
        self.rect=rect
        self.screen.display.blit(self.surface, self.rect)   
    
class Button(TextBox):
    showTextBox=TextBox.show
    def __init__(self,action,center,font,text,color=WHITE,K_BUTTON=None):
        TextBox.__init__(self,center,font,text,color)
        self.center=center
        self.action=action
        self.K_BUTTON=K_BUTTON

    def show(self):
        self.showTextBox()
        if self.state : 
            pygame.draw.polygon(self.screen.display, self.color, [
                self.rect.topleft,
                (self.rect.left-self.rect.height/2,self.rect.centery),
                self.rect.bottomleft], 0)
            pygame.draw.polygon(self.screen.display, self.color, [
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
                self.action()
        if event.type==KEYDOWN:
            if (event.key == K_RETURN and self.state) or (event.key == self.K_BUTTON):
                self.action()

class Parameter:
    def __init__(self,name,span=['OFF','ON'],cur=0):
        self.name=name
        self.span=span
        self.cur=cur
        self.last=len(span)-1
        self.value=span[self.cur]

    def next(self):
        self.cur=min(self.cur+1,self.last)
        self.value=self.span[self.cur]

    def prev(self):
        self.cur=max(self.cur-1,0)
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

class Line(Element):
    def __init__(self,start,end,color=lineColor):
        self.start=start
        self.end=end
        self.color=color

    def show(self):
        pygame.draw.line(self.screen.display, self.color, self.start,self.end,3)

class Enemy(Element):
    def __init__(self,cell,name='A bot',direction=0):
        self.cell=cell
        self.color=enemyColor
        self.size=self.cell.size
        self.direction=direction
        self.been={cell:1}
        self.name=name

    def handle(self,event):
        if event.type==ENEMYMOVE:
            if self.cell.object == EXIT:
                you_win(self)
            c=self.cell
            b=self.been[c]
            d={False:[],True:[c]}
            for n in c.doors:
                if n:
                    d[n in self.been.keys()].append(n)
            if d[False]:
                l=d[False]
                n=l[int(rnd()*len(l))]
            else:
                for m in d[True]:
                    if self.been[m] <= b:
                        n=m
                        b=self.been[m]
            self.cell=n
            self.been[n]=b+1

        
    def corners(self):
        cx,cy=self.cell.center
        sx,sy=self.size
        return [
            (cx,cy+sy-1),
            (cx+sx-1,cy),
            (cx,cy-sy+1),
            (cx-sx+1,cy)]

    def show(self):
        if self.cell.visible>1:
            pygame.draw.polygon(self.screen.display, enemyColor, self.corners())
        # for line in self.track:
        #     line.show()

    def __str__(self):
        return self.name


        
                    
class Player(Element):
    def __init__(self,cell,controls,name,color=playerColor):
        self.cell=cell
        d={
            'HEXAGON':[0,1,2,3,4,5],
            'SQUARE': [1,1,0,3,3,2]
            # 'HEXAGON':[0,1,2,3,4,5,3,1],
            # 'SQUARE': [0,0,1,2,2,3,2,0]

            }[cell.shape]
        self.control=dict(zip(controls,d))
        self.name=name
        self.color=color
        self.size=self.cell.size
        self.track=[]


    def handle(self,event):
        if event.type==KEYDOWN :
            if event.key in self.control.keys():
                d=self.control[event.key]
                self.direction=d
                for i in range(self.cell.sides):
                    n=self.cell 
                    while n: 
                        n.visible=0 if (amap.value=='empty') else 1
                        n=n.doors[i] 
                nc=self.cell.doors[d]
                if nc:
                    if self.track:
                        self.track.append(Line(self.cell.center,nc.center))
                    self.cell=nc
                self.cell.visible=2
                if self.cell.object == EXIT:
                    you_win(self)
                for i in range(self.cell.sides):
                    n=self.cell.doors[i] if lights.value!='nothing' else False
                    while n: 
                        n.visible=2 
                        n=n.doors[i] if lights.value=='flashlight' else False
            if event.key == K_t:
                if self.track : 
                    self.track=[]
                else :
                    self.track=[Element()]
            


    def corners(self):
        cx,cy=self.cell.center
        sx,sy=self.size
        return [
            (cx,cy+sy-1),
            (cx+sx-1,cy),
            (cx,cy-sy+1),
            (cx-sx+1,cy)]

    def show(self):
        pygame.draw.polygon(self.screen.display, self.color, self.corners())
        for line in self.track:
            line.show()

    def __str__(self):
        return self.name
   
class Cell(Element):
    def __init__(self,center,size,shape,vis=1,obj=EMPTY):
        self.sides={'H':6,'S':4}[shape[0]]
        self.doors=[False]*self.sides
        self.shape=shape
        self.center=center
        self.size=size
        self.visible=vis
        self.object=obj
        cx,cy=center
        sx,sy=size
        self.corners={
            'HEXAGON':[
                (cx-sx,cy),
                (cx-sx/2,cy-sy),
                (cx+sx/2,cy-sy),
                (cx+sx,cy),
                (cx+sx/2,cy+sy),
                (cx-sx/2,cy+sy),
                ]
                ,
            'SQUARE':[
                (cx-sx,cy-sy),
                (cx-sx,cy+sy),
                (cx+sx,cy+sy),
                (cx+sx,cy-sy),
                ]
        }[shape]
        

    def show(self):
        # print self.sides,self.corners
        if self.visible:
            pygame.draw.polygon(self.screen.display, floorColor[self.visible], self.corners,0)
            for i in range(self.sides):
                if not self.doors[i]:
                    pygame.draw.line(self.screen.display, wallColor, self.corners[i-1],self.corners[i],1)
                # else:
                    # pygame.draw.line(self.screen.display,(244,0,0), self.corners[i-1],self.corners[i],2)
            if self.object==EXIT:
                pygame.draw.circle(self.screen.display,exitColor, self.center, min(self.size),0)
                    
class Field(Element):
    def __init__(self,size,shape,cycles=0):
        s=size
        n=2*s-1
        a={'H':6,'S':4}[shape[0]]
        self.sides=a
        self.radius=s
        self.diameter=n
        self.shape=shape
        self.cell_size={
            'HEXAGON':((2*self.screen.display_width)/(3*n),(self.screen.display_height)/(2*n)),
            'SQUARE':(self.screen.display_width/(2*n),self.screen.display_height/(2*n))}[shape]
        self.cells={}

        walls=0
        doors=[]
        component={}
        for i in range(n):
            for j in range(n):
                if not self.out(i,j):
                    self.cells[(i,j)]=Cell(self.coords(i,j),self.cell_size,shape=shape,vis=(amap.value=='full'))
                    component[(i,j)]=0
                    walls+=1
                    for d in range(a):
                        doors.append((i,j,d))

        shuffle(doors)
        components=[[]]
        e=(0,0)
        for i1,j1,d in doors[:]:
            i2,j2=further(i1,j1,d,a)
            if self.out(i2,j2):
                e=(i1,j1)
            else:
                d1,d2=d,(d+a/2)%a
                c1,c2=component[(i1,j1)],component[(i2,j2)]
                if not (c1==c2 >0) :
                    # c11=self.cells[(i1,j1)]
                    # c22=self.cells[(i2,j2)]
                    self.cells[(i1,j1)].doors[d1]=self.cells[(i2,j2)]
                    self.cells[(i2,j2)].doors[d2]=self.cells[(i1,j1)]
                    # self.cells[walls]=Line(c11.center,c22.center)
                    walls-=1
                    # c1,c2=min(c2,c1),max(c1,c2)    
                    if c2==c1==0:
                        kc=len(components)
                        components.append([(i1,j1),(i2,j2)])
                        component[(i1,j1)]=kc
                        component[(i2,j2)]=kc
                    elif c1==0:
                        components[c2].append((i1,j1))
                        component[(i1,j1)]=c2 
                    elif c2==0:
                        components[c1].append((i2,j2))
                        component[(i2,j2)]=c1     
                    else:
                        for ki,kj in components[c1]:
                            component[(ki,kj)]=c2 
                            components[c2].append((ki,kj))
                        components[c1]=[]
                # else :
                #     walls.append()
                if walls == 1 : break
        else : print "walls error", walls 
        self.cells[e].object=EXIT  
        shuffle(doors) 
        for i1,j1,d in doors[:]:
            if not cycles: break
            i2,j2=further(i1,j1,d,a)
            d1,d2=d,(d+a/2)%a 
            if self.cells[(i1,j1)].doors[d]==False and (not self.out(i2,j2)):
                cycles-=1
                self.cells[(i1,j1)].doors[d1]=self.cells[(i2,j2)]
                self.cells[(i2,j2)].doors[d2]=self.cells[(i1,j1)]
        else: print "there are no walls left"



    def out(self,i,j):
        s=self.radius
        n=self.diameter
        if i<0 or j<0: return True
        if i>=n or j>=n: return True
        if self.shape=='HEXAGON':
            if i>=s and j<=i-s : return True
            if j>=s and i<=j-s : return True
        return False

    def coords(self,i,j):
        n=self.diameter
        dw=(self.screen.display_width/n)*n
        ddw=(self.screen.display_width-dw)/2
        dh=(self.screen.display_height/n)*n
        ddh=(self.screen.display_height-dh)/2
        return {
            'HEXAGON':(ddw+dw/(2*n)+j*dw/(n),ddh+dh/(4*n)+dh/4+i*dh/(n)-dh*j/2/(n)),
            'SQUARE':(ddw+dw/(2*n)+i*dw/(n),ddh+dh/(2*n)+j*dh/(n))
            }[self.shape]
        # return {
            # 'HEXAGON':(ddw+dw/(4*n)+dw/4+i*dw/(n)-dw*j/2/(n),ddh+dh/(2*n)+j*dh/(n)),
            # 'SQUARE':(ddw+dw/(2*n)+i*dw/(n),dh/(2*n)+j*dh/(n)+ddh)
            # }[self.shape]


    def show(self):
        for cell in self.cells.values():
            cell.show()

if True: # Parameters   
    fiblist = [0,1,2]
    sizes = [3]
    for i in range(17):
        fiblist.append(fiblist[-1]+fiblist[-2])
        sizes.append(sizes[-1]+i/4+1)
    size = Parameter('Field size',sizes,8)
    cycles = Parameter('Extra appertures',fiblist)
    shape = Parameter('Shape',['SQUARE','HEXAGON'])
    players =Parameter('Number of players',[1,2,3])
    enemies =Parameter('Number of bots',range(5))
    speed=Parameter("Bots' speed",range(1,5))
    lights = Parameter('Light',['flashlight','torch','nothing',])
    amap = Parameter('Map',['full','dynamic','empty'])
    


if True: # state changers
    def to_menu():
        game.fill(menuContent)
        
    def from_scratch(): 
        pygame.time.set_timer(ENEMYMOVE,{
            1:1000,
            2:500,
            3:200,
            4:100,
            }[speed.value]) 
        
        s=size.value-1
        f=Field(size.value,shape.value,cycles.value)
        e=[Enemy(f.cells[(s,s)]) for k in range(enemies.value) ]

        # f.cells[(0,0)].object=EXIT
        # cs=f.cells.values()
        p=[]
        for k in range(players.value):
            c=f.cells[(s,s)]#cs[int(rnd()*len(cs))]
            c.visible=True
            # e=Cell(c.center,(s,s),c.shape)
            # e.doors=[c]*10
            p.append(Player(c,controlkeys[k],"Player "+str(k+1),playerColors[k]))
        gameContent.elements=[Button(to_menu,(0, 0),fontOption," ",K_BUTTON=K_ESCAPE),f]+e+p
        game.fill(gameContent)

    def you_win(element):
        congratsContent.elements[-1]=TextBox((wc, hc-2*sizeCaption),fontCaption,str(element),element.color)
        game.fill(congratsContent)

    def to_options():
        game.fill(optionsContent)

    def close():
        pygame.quit()
        quit()

    def to_game():
        game.fill(gameContent)

    def to_info():
        game.fill(infoContent)

    def to_participants():
        game.fill(participantsContent)

    def to_map():
        game.fill(mapContent)

 
if True: # states' contents  
    wc=mainScreen.display_width/2
    hc=mainScreen.display_height/2

    mapContent = Content([
            Menu([
                Option(shape,(wc,hc-sizeOption),fontOption),
                Option(size,(wc,hc),fontOption),
                Option(cycles,(wc,hc+sizeOption),fontOption),
                Option(amap,(wc, hc+2*sizeOption),fontOption),
                Button(to_options,(wc, hc+3*sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
            TextBox((wc, hc-2*sizeCaption),fontCaption,"Map")])
    
    participantsContent = Content([
            Menu([
                Option(players,(wc, hc-sizeOption),fontOption),
                Option(lights,(wc, hc),fontOption),
                Option(enemies,(wc,hc+sizeOption),fontOption),
                Option(speed,(wc, hc+2*sizeOption),fontOption),
                Button(to_options,(wc, hc+3*sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
            TextBox((wc, hc-2*sizeCaption),fontCaption,"Participants")])


    optionsContent = Content([
            Menu([
                Button(to_map,(wc, hc-sizeOption),fontOption,"MAP",K_BUTTON=K_m),
                Button(to_participants,(wc, hc),fontOption,"PARTICIPANTS",K_BUTTON=K_p),
                Button(to_menu,(wc, hc+sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
            TextBox((wc, hc-2*sizeCaption),fontCaption,"Options")])
            
    menuContent=Content([
            Menu([Button(from_scratch,(wc, hc-sizeOption),fontOption,"PLAY",K_BUTTON=K_p),
                Button(to_options,(wc, hc),fontOption,"OPTIONS",K_BUTTON=K_o),
                Button(to_info,(wc, hc+sizeOption),fontOption,"INFO",K_BUTTON=K_i),                
                Button(close,(wc, hc+2*sizeOption),fontOption,"QUIT",K_BUTTON=K_ESCAPE)]),
            TextBox((wc, hc-2*sizeCaption),fontCaption,"Menu")])
            
    congratsContent=Content([
            Menu([Button(from_scratch,(wc, hc),fontOption,"REPLAY"),
                Button(to_game,(wc, hc+sizeOption),fontOption,"CONTINUE",K_BUTTON=K_ESCAPE),
                Button(to_menu,(wc, hc+2*sizeOption),fontOption,"EXIT",K_BUTTON=K_ESCAPE),]),
            TextBox((wc, hc-sizeCaption),fontCaption,"has found the way out!"),
            TextBox((wc, hc-2*sizeCaption),fontCaption,"Somebody")])
    
    infoContent=Content([
            TextBox((wc, hc-3*sizeText),fontText,"Red players' control keys are QWEASD"),
            TextBox((wc, hc-2*sizeText),fontText,"Green players' control keys are UIOJKL"),
            TextBox((wc, hc-1*sizeText),fontText,"Blue players' control keys are 4-9 on the NumPad "),
            TextBox((wc, hc),fontText,"The goal is to reach the way out of the maze."),
            TextBox((wc, hc+sizeText),fontText,"The exit is on the one of field sides."),
            Menu([Button(to_menu,(wc, hc+2*sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
        ])
    gameContent=Content([])
            
to_menu()
game.play() 



