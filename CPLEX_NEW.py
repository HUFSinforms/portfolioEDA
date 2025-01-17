import cplex
from cplex.exceptions import CplexError
import sys
import numpy as np
import time


class portfolio():
    def __init__(self, sector, bench, asset, MCAPQ, beta, alpha,w_pre,O_scale):
        self.pluschek = 0
        self.w_upchek = 0
        self.q1num = 0
        self.c = cplex.Cplex()
        self.t = self.c.variables.type
        self.asset = asset
        self.alpha = alpha
        self.bench = bench
        self.w_pre = w_pre
        self.O_scale = O_scale
        
        
        self.c.objective.set_sense(self.c.objective.sense.minimize)

        self.c.variables.add(names=["d" + str(i) for i in asset], obj=alpha, lb=[-1 * bench[j] for j in asset])
        
        

        self.c.variables.add(names=["assum"], lb=[-99999])
        
        
        
        self.c.variables.add(names=["O"], obj=[O_scale], lb=[-99999])
        
        
        self.c.variables.add(names=["dx" + str(i) for i in w_pre.keys()], lb=[0 for j in w_pre.keys()],ub=[50000 for j in w_pre.keys()])
        
        

        # print(c.variables.get_lower_bounds())


        # c.variables.add(names=["y"+str(i) for i in asset],lb=[-99999999 for j in asset])
        #
        # c.variables.add(names=["c"+ str(j) + str(i) for j in asset for i in range(2)], types=[t.binary for i in asset for j in range(2)])



        # c.linear_constraints.add(
        #     lin_expr=[cplex.SparsePair(ind=["assum"], val=[1.0])], senses=["E"],
        #     rhs=[returns], names=["sum"])
        
        O_rhs = 0
        


        for i in asset:
            self.c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["d" + str(i)], val=[1.0])], senses=["G"],
                                          rhs=[-1 * bench[i]], names=[str(i) + "di_wi"])
            # c.linear_constraints.set_linear_components(str(i)+"di_wi", [["w" + str(i)], [1.0]])
            self.c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["d" + str(i)], val=[1.0])], senses=["L"],
                                          rhs=[0.05], names=["st_5_1"])
            self.c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["d" + str(i)], val=[1.0])], senses=["G"],
                                          rhs=[-0.05], names=["st_5_2"])
            
            if i not in w_pre.keys():
                O_rhs = O_rhs - bench[i]
                
                
        self.c.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = ["dx"+str(i) for i in w_pre.keys()], val = [1.0]*len(w_pre.keys()))],senses=["E"],rhs=[O_rhs],names=["TurnOver"])
        
        self.c.linear_constraints.set_linear_components("TurnOver", [["O"], [-1.0]])       
        
        for i in asset:
            if i not in w_pre.keys():
                self.c.linear_constraints.set_linear_components("TurnOver", [["d"+ str(i)], [1.0]])
            
            
        for i in w_pre.keys():
            if i in asset:
                self.c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["dx" + str(i)], val=[1.0])], senses=["G"],
                                              rhs=[1*((-1 * bench[i])+w_pre[i])], names=[str(i) + "dx"])

                self.c.linear_constraints.set_linear_components(str(i) + "dx", [["d"+ str(i)], [1.0]])

                self.c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["dx" + str(i)], val=[1.0])], senses=["G"],
                                              rhs=[1*(bench[i]-w_pre[i])], names=[str(i) + "dx2"])

                self.c.linear_constraints.set_linear_components(str(i) + "dx2", [["d"+ str(i)], [-1.0]])
                
            else:
                
                self.c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["dx" + str(i)], val=[1.0])], senses=["G"],
                                              rhs=[1*w_pre[i]], names=[str(i) + "dx"])
                
                
                self.c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=["dx" + str(i)], val=[1.0])], senses=["G"],
                                              rhs=[-1*w_pre[i]], names=[str(i) + "dx2"])

        
        # bench_sum = 0
        #
        # for i in bench:
        #     bench_sum += bench[i]

        # print(bench_sum)

        self.c.linear_constraints.add(lin_expr = [cplex.SparsePair(ind = ["d"+str(i) for i in asset], val = [1.0]*len(asset))],senses=["E"],rhs=[0],names=["st_4"])
        
        
        

        for j in sector:
            self.c.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in sector[j]], val=[1.0] * len(sector[j]))],
                senses=["L"],
                rhs=[0.1], names=["st_6_1"])
            self.c.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in sector[j]], val=[1.0] * len(sector[j]))],
                senses=["G"],
                rhs=[-0.1], names=["st_6_2"])

        for j in MCAPQ:
            self.c.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in MCAPQ[j]], val=[1.0] * len(MCAPQ[j]))],
                senses=["L"],
                rhs=[0.1], names=["st_7_1"])
            self.c.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in MCAPQ[j]], val=[1.0] * len(MCAPQ[j]))],
                senses=["G"],
                rhs=[-0.1], names=["st_7_2"])

        self.c.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in asset], val=[beta[i] for i in asset])], senses=["L"],
            rhs=[0.1], names=["st_8_1"])
        self.c.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in asset], val=[beta[i] for i in asset])], senses=["G"],
            rhs=[-0.1], names=["st_8_2"])





    def set_upsum(self,w_upsums, big_w_dic):
        #print(self.w_upchek," upchek num")
        if self.w_upchek > 0:
            self.c.linear_constraints.delete("sum")
            self.c.linear_constraints.delete("w_big")

        self.c.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in self.asset], val=self.alpha)], senses=["E"],
            rhs=[0.0], names=["sum"])
        self.c.linear_constraints.set_linear_components("sum", [["assum"], [-1.0]])

        # 0.112046486647
        # -0.07957269716079549

        bigeer_bench_sum = 0
        for i in self.asset:
            bigeer_bench_sum = bigeer_bench_sum + self.bench[i] * big_w_dic[i]

        self.c.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=["d" + str(i) for i in self.asset], val=[big_w_dic[i] for i in self.asset])],
            senses=["G"],
            rhs=[w_upsums - bigeer_bench_sum], names=["w_big"])

        self.w_upchek += 1

    def set_con(self,sols):

        nums = 0
        if self.pluschek > 0:
            for i in self.asset:
                self.c.linear_constraints.delete("st_select" + str(i))
        for i in self.asset:
            if nums in sols:
                self.c.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=["d" + str(i)], val=[1.0])], senses=["G"],
                    rhs=[-1 * self.bench[i] + 0.00101], names=["st_select" + str(i)])

            else:
                self.c.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=["d" + str(i)], val=[1.0])], senses=["E"],
                    rhs=[-1 * self.bench[i]], names=["st_select" + str(i)])
            nums += 1
        self.pluschek += 1







            # c.linear_constraints.add(
            #     lin_expr=[cplex.SparsePair(ind=["q" + str(i) for i in asset], val=[1.0]*len(asset))], senses=["G"],
            #     rhs=[50], names=["st_9_1"])
            #
            #
            # c.linear_constraints.add(
            #     lin_expr=[cplex.SparsePair(ind=["q" + str(i) for i in asset], val=[1.0]*len(asset))], senses=["L"],
            #     rhs=[70], names=["st_9_2"])

            # c.linear_constraints.add(
            #     lin_expr=[cplex.SparsePair(ind=["y" + str(i) for i in asset], val=[1.0] * len(asset))], senses=["G"],
            #     rhs=[0], names=["st_10_1"])
            #
            # c.linear_constraints.add(
            #     lin_expr=[cplex.SparsePair(ind=["y" + str(i) for i in asset], val=[1.0] * len(asset))], senses=["L"],
            #     rhs=[0.4], names=["st_10_2"])



            # for i in asset:
            #     Q = cplex.SparseTriple(ind1=["q"+str(i)], ind2=["d"+str(i),"z"+str(i)],
            #                        val=[-1.0,1.0])
            #     c.quadratic_constraints.add(rhs=bench[i], quad_expr=Q, name="Q"+str(i))
            # #
            # Q2 = cplex.SparseTriple(ind1=["q" + str(i) for i in asset], ind2=["d" + str(i) for i in asset],
            #                        val=[-1.0]*len(asset))
            # c.quadratic_constraints.add(rhs=0.6, quad_expr=Q2, name="st_10_2", sense="G")

    def quard_con(self,Q_con, multiple):
        if self.q1num > 0:
            self.c.quadratic_constraints.delete("st_11_1")
        Q3 = cplex.SparseTriple(ind1=Q_con[0], ind2=Q_con[1], val=Q_con[2])
        self.c.quadratic_constraints.add(rhs=0.01 * multiple, quad_expr=Q3, name="st_11_1", sense="L")
        self.q1num += 1

    # c.linear_constraints.add(
    #     lin_expr=[cplex.SparsePair(ind=["z" + str(i) for i in asset], val=[-1.0 for i in asset])], senses=["G"],
    #     rhs=[-0.4], names=["st_10_2"])


    def quard_obj(self,qmat):
        
        
        self.c.objective.set_quadratic(qmat)

        



    def solves(self):
        self.c.parameters.threads.set(1)
        self.c.set_log_stream(None)
        self.c.set_error_stream(None)
        self.c.set_warning_stream(None)
        self.c.set_results_stream(None)
        #self.c.write('TO_1.lp')
        

        self.c.solve()
        
        
        
        
        #print("optimal")
        
        #print(self.c.solution.get_status())


        abcd = []
        ab = {}
        cd = {}
        ef={}
        

        numa = 0
        for i in self.asset:

           # print("d" + str(i)  + " : " + str(self.c.solution.get_values("d" + str(i))))
            # if self.bench[i] + self.c.solution.get_values("d" + str(i)) > 0:
            # print("w" + str(i)  + " : " + str(bench[i] + self.c.solution.get_values("d" + str(i))))
            # print(numa)
            # print("q" + str(i) + " : " + str(c.solution.get_values("q" + str(i))))
            ab.update({str(i): self.bench[i] + self.c.solution.get_values("d" + str(i))})

            cd.update({str(i): self.c.solution.get_values("d" + str(i))})
            
            ef.update({str(i):self.c.solution.get_reduced_costs("d" + str(i))})
            numa += 1
            #    print("assum"+ " : " + str( c.solution.get_values("assum" )))
            #    print(c.solution.get_objective_value())
            #    print(c.solution.get_quadratic_slacks())
        abcd.append(ab)
        abcd.append(cd)
        abcd.append(self.c.solution.get_objective_value())
        abcd.append(ef)
        abcd.append(self.c.solution.get_status())
        print("O"  + " : " + str(self.c.solution.get_values("O")))
        print(self.c.solution.get_objective_value())

        #for j in self.w_pre.keys():
            #print("dx"+ str(j)  + " : " + str(0.0001*self.c.solution.get_values("dx"+ str(j))))
           # if j in self.asset:
               # print("dx"+ str(j)  + " 제약식 우변1 : " + str(self.bench[j]+self.c.solution.get_values("d"+ str(j))-self.w_pre[j]))
                #print("dx"+ str(j)  + " 제약식 우변2 : " + str(self.w_pre[j]-self.bench[j]-self.c.solution.get_values("d"+ str(j))))
        #if self.O_scale > 0:
           # if self.c.solution.get_values("O") > 10:
                
              #  print("멈춰!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
               # return 1234
        return abcd