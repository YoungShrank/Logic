## flow
1. organize folders as follow
  ```
  base/
      backend_logic_y2/
      Structure/
  ```

2. modify search paths

  - for vscode
    
    modify search paths that claimed in `backend-logicy2.code-workspace`
  - for python
  
    modify search paths claimed in `test.py` (change `"D:/WorkPlace/github"` to your basedir)

3. modify and run `test.py`
  
   modify to choose test for run and then run it


## what's new
### improvement of assumption deduction rule
current assumption rule is rather simple.
1. introduce an assumption if needed
2. deduce base under assumptions (eg. `{a1, a2,..,an}`)
3. reduce assumptions to generate a new conclusioin `a1^ a2^..^an -> c`


this rule is limited in follow scences:
1. i want to retain some assumptions(and derived conclusions) to use to perform further deductions.


the solution is to maintain a stack of assumptions, and introduce the concept of *assumption domain*.
each time we introduce an assumption, we go deep in domains.conversely when we reduce it, we go back to the upper domain.

### record of proof steps 

in the short term, this feature can allow user see where they are in the proof process and
how the conclusions come to what they are.
in the future, record can be use to reoccur the proof process, as an example of digitalization of proof.



### more powerful type deduction
type deduction is specific to the deep meaning of sentence, so absolute type deduction is always imposible.
here, we mainlly try to solve  type of *element representative* `{x:N,| x>1}`   


as rules are based on type, flexible type deduction is never said to be unnecessary. we will introduce *dynamic type deduction* performed by user.




### more robust process

last, to avoid system breakdown or incorrect system state, we will try to handle underlying exceptions during proof.



## example  

`∀Q:Func[N, Prop], P:Func[N, Prop], ((∀x:N, Q(x) → P(x) ) →((∀x:N, Q(x)) →(∀x:N, P(x))))`

     

