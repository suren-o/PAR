#implementing Strips

stack = [] #this is a list, stack = [goal] + stack (thats how we push), stack = stack[1:] (thats how we remove)
state_list = [] #this is going to be a 2d array that contains all the information about the state
operator_plan = [] #this is going to contain a plan of which operators to carry out

#input data
inputdata = input("Please enter the file name for the planner: ")
#read the files
f = open(inputdata, 'r').read().split("\n") #an array with 2 things, the first line of text, the second line of text
#the first line: InitialState=Robot-location(o1);Machine(o4,3);Machine(o8,1); Machine(o21,2);Machine(o23,1);Machine(o31,2);Petition(o3,1); Petition(o11,3);Petition(o12,1);Petition(o13,2);Petition(o25,1);
#the second line:GoalState=Robot-location(o7);Served(o3);Served(o11);Served(o12); Served(o13);Served(o25);
f[0] = f[0][13:]
f[1] = f[1][10:]

#so now that they are trimmed we want to split the lines up by the ";"
f[0] = f[0].split(";")
f[1] = f[1].split(";")

i = 0
while i < len(f[0]):
  f[0][i] = f[0][i].strip()
  i+=1

i = 0
while i < len(f[1]):
  f[1][i] = f[1][i].strip()
  i+=1

#if you look at f[0], and f[1] they have an extra '' in the back so we need to take it out

f[1].pop(len(f[1])-1)
f[0].pop(len(f[0])-1)

#stripping out the o's 
i = 0
while i < len(f[0]):
  temp = f[0][i].split("(")
  f[0][i] = temp[0] + "(" + temp[1][1:] #except the first character which we know to be an 'o'
  i+=1

i = 0
while i < len(f[1]):
  temp = f[1][i].split("(")
  f[1][i] = temp[0] + "(" + temp[1][1:] #except the first character which we know to be an 'o'
  i+=1


# print(f)

state_list = f[0] #the initial state
stack = f[1] #these go on the stack
stack.reverse() #to reverse it 
operator_plan = [] #this is going to contain a plan of which operators to carry out
steps = 0 #this is just a variable that keeps track of how many steps we have walked 
location = eval(state_list[0][14:]) #this gets us our location 
#time to run strips 

while len(stack) > 0: #while stack is not empty
  #grab top the stack
  top = stack[0]

    
  #lets make a rule a string prefixed by op: is an operator 
  somerules='''
    "op:Make(o,n)" is an operator, preconditions: robot-location(o), robot-free, machine(o,n), activity
    "op:Serve(o,n)" is an operator, preconditions:robot-location(o1),steps(x), activity
    "op:Move(o1,o2)" is an opeartor, preconditions:, activity
  
  '''
  
  if top in state_list: #if the condition at the top is in
    stack = stack[1:] #this removes the top element
    continue #then don't do anything
  elif top[:3] != "op:": #so if the current string is NOT an operator

    
    #remember to REMOVE the final operators from stack
    #remember to STORE the operators detected
    #we need to id if top (the goal) is either robot-locatio, robot-free, etc...
    #then depending on which it is, we need to add the correct things to the stack 
    
    if top[:14] == "Robot-location":
      stack = stack[1:] #take off the first element of the stack
      #i want to now add a move command 
      #i can do a complete search for robot location in the state list 
      #or i can make ONE more variable, called location, that just stores the location
      #the latter is a better idea, it doesn't take as much time
     
      stack = ["op:Move(" + str(location) + "," + str(eval(top[14:])) + ")"] + stack
      
    if top[:10] == "Robot-free":
      print("believed-unncessary")
      #not an issue at the moment 
    
    if top[:12] == "Robot-loaded":
      print("believed-unncesary")
      #not an issue at the moment 
      
    if top[:6] == "Served":
      stack = stack[1:] #take off the top of the stack
      
      payload = ""
      for data in state_list:
        if "Petition(" + str(eval(top[6:])) + "," in data:  #if petition(23 for example, an incpmlete string
          payload = data
          break
      pair = eval(payload[8:])
      #number of cups of coffee is pair[1]
      machine_list = [] #to be filled with machines
      running_min = 100000 #this is going to be the running min or closest machine
      running_location = 99999 #this is going to be the locatino of closest machine
      for data in state_list:
        
        
        if data[:7] == "Machine":
          pairdata = eval(data[7:])
          if pairdata[1] == pair[1]: 
          #we need to compute distance from our current location
            vertical = abs(int((pairdata[0] -1)/6) - int((location-1)/6))
            horizontal = abs((pairdata[0]-1)%6 - (location-1)%6)
          
            if vertical + horizontal < running_min:
              running_min = vertical + horizontal #update to the new machine 
              running_location = pairdata[0] #this is the new location of that machine 
      goal = '''    
      robot-location(o2) #we need to go to location o2    
      "op:Make(o2,n)" #it needs to make n cups of coffee at location o2
      robot-location(o) #on the list
      "op:Serve(o1,n)" #needs to be added
      '''
      
      stack = ["Robot-location(" + str(running_location) + ")",
                "op:Make("+str(running_location)+","+str(pair[1])+")",    
                "op:Move("+ str(running_location) + "," + str(pair[0])+")", 
                "op:Serve("+str(pair[0]) + "," + str(pair[1]) + ")"] + stack
      
    
  elif top[:3] == "op:": #so the current string IS an operator
  
    #take it off the stack
    
    stack = stack[1:] #one thing off
    print(top)
    operator_plan.append(top)
    if top[:7] == "op:Make":
      #if its make it is of the form op:Make(o,n)
      #so that means we want to grab the (o,n) and actually parse those numbers 
      top = top[7:] #this should remove characters 
      pair = eval(top) #this is a trick to actually evaluate the pair as if it were code giving us o,n
 
      #so this changes the state accordingly, remember that pair = [pair[0], pair[1]] = (o,n)
      try:
        state_list.remove("Robot-free")
      except:
        print("Robot-Free couldn't be removed")
      state_list.append("Robot-loaded(" + str(pair[1]) + ")")
      
      
    if top[:8] == "op:Serve":
      top = top[8:]
      pair = eval(top)
      #o Add:served(o),robot-free
      #o Delete:petition(o,n),robot-loaded(n)
      
      state_list.append("Robot-free")
      state_list.append("Served(" + str(pair[0]) + ")")

      try:      
        state_list.remove("Petition"+top)
        state_list.remove("Robot-loaded(" + str(pair[1]) + ")")
      except:
        print("Something here couldn't be removed")
    
    if top[:7] == "op:Move":
      top = top[7:]
      pair = eval(top) #now grabbing locatoins
      #o Add:robot-location(o2),steps(x+distance(o1,o2)) 
      #o Delete:robot-location(o1),steps(x)
      
      state_list.append("Robot-location("+str(pair[1]) + ")")
      location = pair[1] #so this keeps track of our change in location 

      try:
        state_list.remove("Robot-location("+str(pair[0])+ ")")
      except:
        print("Robot-location("+str(pair[0]) + ") could not be removed")

      aer = [0,0] #for assignment
      #given a location o1, int(o1/6) is the vertical layer, and (o1-1)%6 is the horizontal layer
      aer[0] = [int((pair[0]-1)/6), (pair[0]-1)%6]
      aer[1] = [int((pair[1]-1)/6), (pair[1]-1)%6]
      
      #so now distance is simply reflected
      steps += abs(aer[0][0] - aer[1][0])
      steps += abs(aer[0][1] - aer[1][1])    
          
print("The required steps: " + str(steps))
print("The Robot's plan: " + str(operator_plan))     