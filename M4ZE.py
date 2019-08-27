if True: # import and init
    from numpy import zeros,sqrt,sin,cos,array,sum,prod,dtype
    from random import choice, shuffle
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
    wallColor = (150,200,0)
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
            size = (int(infoObject.current_w*0.9), int(infoObject.current_h*0.9))
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

    def isInside(self,x,y,z,t):
        return x>=0 and x<self.Width  and y>=0 and y<self.Height and z>=0 and z<self.Depth and t>=0 and t<self.Fourth


    def __init__(self, Width = 5, Height = 5, Depth = 5, Fourth = 5, mazetype = 'labyrinth', vis = None, extra = 0.0 ):
        self.mazetype = mazetype
        self.Width = Width
        self.Height = Height
        self.Depth = Depth
        self.Fourth = Fourth

        self.vis = vis

        self.dims = array([Width, Height, Depth, Fourth],dtype = int)
        self.size = prod(self.dims)

        self.pos = array([0,0,Depth-1,Fourth-1],dtype = int)
        
        self.exit = array([Width-1,Height-1,0,0],dtype = int)
        
        self.walls = zeros(self.dims,dtype = int)
        
        visited = zeros(self.dims,dtype = int) 
        self.visited =  zeros(self.dims,dtype = int)



        if mazetype == 'depth-first':
            path = [(choice(range(Width)),choice(range(Height)),choice(range(Depth)),choice(range(Fourth)))]
            while path:
                nexts = []
                x, y, z, t = path[-1] 
                visited[x, y, z, t] = 1
                for xn,yn,zn,tn in [
                    (x+1,y,z,t),(x-1,y,z,t),
                    (x,y+1,z,t),(x,y-1,z,t),
                    (x,y,z+1,t),(x,y,z-1,t),
                    (x,y,z,t+1),(x,y,z,t-1)]:
                    if self.isInside(xn,yn,zn,tn) and visited[xn,yn,zn,tn]<0.5: nexts.append((xn,yn,zn,tn,))
                if nexts:
                    xn,yn,zn,tn = choice(nexts)
                    self.walls[min(x,xn),min(y,yn),min(z,zn),min(t,tn)] += (x-xn)*(x-xn)+2*(y-yn)*(y-yn)+4*(z-zn)*(z-zn)+8*(t-tn)*(t-tn)
                    path.append((xn,yn,zn,tn,))
                else: path.pop()

        elif mazetype == 'breadth-first':
            first = (choice(range(Width)),choice(range(Height)),choice(range(Depth)),choice(range(Fourth)))
            path = {(first,first)}
            self.visited[first]=2
            while path:
                (xn,yn,zn,tn),(x, y, z, t) = path.pop()
                if visited[x,y,z,t]<0.5:
                    self.walls[min(x,xn),min(y,yn),min(z,zn),min(t,tn)] += (x-xn)*(x-xn)+2*(y-yn)*(y-yn)+4*(z-zn)*(z-zn)+8*(t-tn)*(t-tn)
                    for xn,yn,zn,tn in [
                        (x+1,y,z,t),(x-1,y,z,t),
                        (x,y+1,z,t),(x,y-1,z,t),
                        (x,y,z+1,t),(x,y,z-1,t),
                        (x,y,z,t+1),(x,y,z,t-1)]:
                        if self.isInside(xn,yn,zn,tn) and visited[xn,yn,zn,tn]<0.5: path.add( ((x, y, z, t),(xn,yn,zn,tn,),) )
                visited[x, y, z, t] = 1

        elif mazetype == 'random-walks':
            doors = zeros(self.dims,dtype = int) 
            verts = [(i,j,k,l) for i in range(Width) for j in range(Height) for k in range(Depth) for l in range(Fourth)]

            first = verts.pop()
            visited[first] = -1 
            cur = 0

            while verts:

                v = verts.pop() 
                x,y,z,t = v
                doors[x,y,z,t] = -1
                cur +=1 
                while visited[x,y,z,t]>-0.5:
                    visited[x,y,z,t] = cur
                    d =  choice(range(8))
                    xn,yn,zn,tn = [
                        (x+1,y,z,t),(x-1,y,z,t),
                        (x,y+1,z,t),(x,y-1,z,t),
                        (x,y,z+1,t),(x,y,z-1,t),
                        (x,y,z,t+1),(x,y,z,t-1)][d]
                    if self.isInside(xn,yn,zn,tn):
                        x,y,z,t = xn,yn,zn,tn
                        if visited[x,y,z,t]<cur:
                            doors[x,y,z,t]=d

                while doors[x,y,z,t]>-0.5:
                    d = doors[x,y,z,t]
                    xn,yn,zn,tn = [
                        (x-1,y,z,t),(x+1,y,z,t),
                        (x,y-1,z,t),(x,y+1,z,t),
                        (x,y,z-1,t),(x,y,z+1,t),
                        (x,y,z,t-1),(x,y,z,t+1)][d]
                    self.walls[min(x,xn),min(y,yn),min(z,zn),min(t,tn)] += (x-xn)*(x-xn)+2*(y-yn)*(y-yn)+4*(z-zn)*(z-zn)+8*(t-tn)*(t-tn)
                    x,y,z,t = xn,yn,zn,tn 
                    visited[x,y,z,t] = -1 




        elif mazetype == 'random-walls' :
            doors = [(i,j,k,l,d) for i in range(Width) for j in range(Height) for k in range(Depth) for l in range(Fourth) for d in range(4)]
            shuffle(doors)
            rooms = [[]]
            for i1,j1,k1,l1,d in doors:
                # print(visited)
                i2,j2,k2,l2 = [(i1+1,j1,k1,l1),(i1,j1+1,k1,l1),(i1,j1,k1+1,l1),(i1,j1,k1,l1+1)][d]
                dw = [RIGHT, FORWARD, UPWARDS, FASTER][d]
                if self.isInside(i2,j2,k2,l2):
                    self.walls[i1,j1,k1,l1]+=dw
                    v1, v2 = visited[i1,j1,k1,l1], visited[i2,j2,k2,l2]
                    if v1>v2 :
                        i1,j1,k1,l1,v1,i2,j2,k2,l2,v2 = i2,j2,k2,l2,v2,i1,j1,k1,l1,v1
                    if v1==0 :
                        if v2==v1: 
                            visited[i1,j1,k1,l1]=len(rooms)
                            visited[i2,j2,k2,l2]=len(rooms)
                            rooms.append([(i1,j1,k1,l1),(i2,j2,k2,l2)])
                        else: 
                            rooms[v2].append((i1,j1,k1,l1))
                            visited[i1,j1,k1,l1] = v2
                    else:
                        if v2==v1 :
                            self.walls[i1,j1,k1,l1]-=dw
                        else:
                            for i2,j2,k2,l2 in rooms[v2]:
                                visited[i2,j2,k2,l2] = v1
                                rooms[v1].append((i2,j2,k2,l2)) 
        else:
            extra = 2.0

        if extra>0.0:
            doors = [(i,j,k,l,d) for i in range(Width) for j in range(Height) for k in range(Depth) for l in range(Fourth) for d in range(4)]
            shuffle(doors)
            count = int(extra*(self.size*3-sum(self.size/self.dims))  )
            while count and doors:
                i1,j1,k1,l1,d = doors.pop()
                i,j,k,l = [(i1+1,j1,k1,l1),(i1,j1+1,k1,l1),(i1,j1,k1+1,l1),(i1,j1,k1,l1+1)][d]
                dw = [RIGHT, FORWARD, UPWARDS, FASTER][d]
                if not self.walls[i1,j1,k1,l1]&dw and self.isInside(i,j,k,l):
                    self.walls[i1,j1,k1,l1]+=dw
                    count -=1
            print(len(doors))

        

    def handle(self,event):
        if event.type==KEYDOWN:
            if event.key == K_ESCAPE:
                return 'menu'
            if event.key == K_p:
                return 'pause'    
            x,y,z,t = self.pos 
            if event.key == K_d and self.walls[x,y,z,t]&RIGHT:
                self.pos[0] += 1
            if event.key == K_s and self.walls[x,y,z,t]&FORWARD:
                self.pos[1] += 1
            if event.key == K_k and self.walls[x,y,z,t]&UPWARDS:
                self.pos[2] += 1
            if event.key == K_l and self.walls[x,y,z,t]&FASTER:
                self.pos[3] += 1
            if event.key == K_a:
                self.pos[0] -= 1
                x,y,z,t = self.pos
                if not self.walls[x,y,z,t]&RIGHT:
                    self.pos[0] += 1
            if event.key == K_w:
                self.pos[1] -= 1
                x,y,z,t = self.pos
                if not self.walls[x,y,z,t]&FORWARD:
                    self.pos[1] += 1
            if event.key == K_i:
                self.pos[2] -= 1
                x,y,z,t = self.pos
                if not self.walls[x,y,z,t]&UPWARDS:
                    self.pos[2] += 1
            if event.key == K_j:
                self.pos[3] -= 1
                x,y,z,t = self.pos
                if not self.walls[x,y,z,t]&FASTER:
                    self.pos[3] += 1

            if self.vis == 'auto' or (self.vis == 'space' and event.key == K_SPACE): 
                x,y,z,t = self.pos 
                self.visited[x,y,z,t] += 1


        if (self.pos == self.exit).all():
            return 'win'

        return None



    def show(self,screen):
        x,y,z,t = self.pos
        Width = self.Width+self.Fourth
        Height = self.Height+self.Depth
        dx =  min(screen.display_width//Width,(8*screen.display_height)//(9*Height))
        dy =  (9*dx)//8

        wallwidth = 3

        pygame.draw.polygon(screen.display, floorColor, [(0,0),(0,dy*Height),(dx*Width,dy*Height),(dx*Width,0)],0)
            
        if self.vis != "none" :
            for i in range(self.Width):
                for j in range(self.Height):
                    if self.visited[i,j,z,t]>0.5:
                        color = onceColor if self.visited[i,j,z,t]<1.5 else twiceColor
                        pygame.draw.polygon(screen.display, color, [
                            (dx*(i),dy*(j)),
                            (dx*(i),dy*(j+1)),
                            (dx*(i+1),dy*(j+1)),
                            (dx*(i+1),dy*(j))],0)

            for i in range(self.Width):
                for k in range(self.Depth):
                    if self.visited[i,y,k,t]>0.5:
                        color = onceColor if self.visited[i,y,k,t]<1.5 else twiceColor
                        pygame.draw.polygon(screen.display, color, [
                            (dx*(i),dy*(self.Height+k)),
                            (dx*(i),dy*(self.Height+k+1)),
                            (dx*(i+1),dy*(self.Height+k+1)),
                            (dx*(i+1),dy*(self.Height+k))],0)
            
            for l in range(self.Fourth):
                for k in range(self.Depth):
                    if self.visited[x,y,k,l]>0.5:
                        color = onceColor if self.visited[x,y,k,l]<1.5 else twiceColor
                        pygame.draw.polygon(screen.display, color, [
                            (dx*(l+self.Width),dy*(self.Height+k)),
                            (dx*(l+self.Width),dy*(self.Height+k+1)),
                            (dx*(l+self.Width+1),dy*(self.Height+k+1)),
                            (dx*(l+self.Width+1),dy*(self.Height+k))],0)

            for l in range(self.Fourth):
                for j in range(self.Height):
                    if self.visited[x,j,z,l]>0.5:
                        color = onceColor if self.visited[x,j,z,l]<1.5 else twiceColor
                        pygame.draw.polygon(screen.display, color, [
                            (dx*(l+self.Width),dy*(j)),
                            (dx*(l+self.Width),dy*(j+1)),
                            (dx*(l+self.Width+1),dy*(j+1)),
                            (dx*(l+self.Width+1),dy*(j))],0)
        
        if "draw walls":

            for i in range(self.Width):
                for j in range(self.Height):
                    if not self.walls[i,j,z,t]&RIGHT:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(i+1),1+dy*(j+1)),(1+dx*(i+1),1+dy*(j)),wallwidth)
                    if not self.walls[i,j,z,t]&FORWARD:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(i+1),1+dy*(j+1)),(1+dx*(i),1+dy*(j+1)),wallwidth)
            
            
            for i in range(self.Width):
                for k in range(self.Depth):
                    if not self.walls[i,y,k,t]&RIGHT:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(i+1),1+dy*(self.Height+k+1)),(1+dx*(i+1),1+dy*(self.Height+k)),wallwidth)
                    if not self.walls[i,y,k,t]&UPWARDS:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(i+1),1+dy*(self.Height+k+1)),(1+dx*(i),1+dy*(self.Height+k+1)),wallwidth)


            for l in range(self.Fourth):
                for k in range(self.Depth):
                    if not self.walls[x,y,k,l]&FASTER:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(l+self.Width +1 ),1+dy*(self.Height+k+1)),(1+dx*(l+self.Width +1 ),1+dy*(self.Height+k)),wallwidth)
                    if not self.walls[x,y,k,l]&UPWARDS:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(l+self.Width +1 ),1+dy*(self.Height+k+1)),(1+dx*(l+self.Width ),1+dy*(self.Height+k+1)),wallwidth)


            for l in range(self.Fourth):
                for j in range(self.Height):
                    if not self.walls[x,j,z,l]&FASTER:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(l+self.Width +1 ),1+dy*(j+1)),(1+dx*(l+self.Width +1 ),1+dy*(j)),wallwidth)
                    if not self.walls[x,j,z,l]&FORWARD:
                        pygame.draw.line(screen.display, wallColor, (1+dx*(l+self.Width +1 ),1+dy*(j+1)),(1+dx*(l+self.Width ),1+dy*(j+1)),wallwidth)

        if "Draw borders":
            pygame.draw.line(screen.display, thickColor, (dx*Width+wallwidth,dy*Height),(0,dy*Height),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (dx*Width,dy*Height+wallwidth),(dx*Width,0),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (dx*self.Width,0),(dx*self.Width,dy*Height),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (0,dy*self.Height),(dx*Width,dy*self.Height),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (0,0),(0,dy*Height),wallwidth*2)
            pygame.draw.line(screen.display, thickColor, (0,0),(dx*Width,0),wallwidth*2)

        ddx = dx//2
        ddy = dy//2

        if "Draw player":
            pygame.draw.polygon(screen.display, activeColor,[ 
                ( 1 + dx*x, 1 + dy*y+ddy),
                ( 1 + dx*x+ddx, 1 + dy*y+dy),
                ( 1 + dx*x+dx, 1 + dy*y+ddy),
                ( 1 + dx*x+ddx, 1 + dy*y)
            ]  )
            pygame.draw.polygon(screen.display, passiveColor,[ 
                ( 1 + dx*(t + self.Width ), 1 + dy*y+ddy),
                ( 1 + dx*(t + self.Width )+ddx, 1 + dy*y+dy),
                ( 1 + dx*(t + self.Width )+dx, 1 + dy*y+ddy),
                ( 1 + dx*(t + self.Width )+ddx, 1 + dy*y)
            ]  )
            pygame.draw.polygon(screen.display, activeColor,[ 
                ( 1 + dx*(t + self.Width ), 1 + dy*(z+self.Height) +ddy),
                ( 1 + dx*(t + self.Width )+ddx, 1 + dy*(z+self.Height) +dy),
                ( 1 + dx*(t + self.Width )+dx, 1 + dy*(z+self.Height) +ddy),
                ( 1 + dx*(t + self.Width )+ddx, 1 + dy*(z+self.Height) )
            ]  )
            pygame.draw.polygon(screen.display, passiveColor,[ 
                ( 1 + dx*x, 1 + dy*(z+self.Height) +ddy),
                ( 1 + dx*x+ddx, 1 + dy*(z+self.Height) +dy),
                ( 1 + dx*x+dx, 1 + dy*(z+self.Height) +ddy),
                ( 1 + dx*x+ddx, 1 + dy*(z+self.Height) )
            ]  )

        if "Draw aim":
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
            self.width = Parameter('1st',range(1,16),5)
            self.height = Parameter('2nd',range(1,16),5)
            self.depth = Parameter('3rd',range(1,16),1)
            self.fourth = Parameter('4th',range(1,16),1)

            self.cycles = Parameter('% extra ways',[0.,.1,1.,10,50,99])
            self.vis = Parameter('Paint',['auto','space','none'])

            self.shape = Parameter('Build',['breadth-first','depth-first','random-walls','random-walks','empty'])

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
                        Button("menu",(wc, hc+3*sizeOption),fontOption,"BACK",K_BUTTON=K_ESCAPE)]),
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
