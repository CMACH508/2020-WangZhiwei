import mcts
from play import MCTSPlayer
import network
import hex
import gtp
import sys

def make_engine(net):
    instance = MCTSPlayer(net, simulations_per_move=1600, num_parallel=1, th=0)
    #instance = CGOSPlayerMixin(network=net)
    instance.initialize_game()
    engine = gtp.Engine(instance)
    return engine

if __name__ == '__main__':
    net = network.PV('zero310000.model')

    engine = make_engine(net)
    #sys.stderr.write("GTP engine ready\n")
    #sys.stderr.flush()

    flag = 0
    while not engine.disconnect:
        instruction = input()
        flag += 1
        try:
            cmd_list = instruction.split("\n")
            print("cmd_list", cmd_list)
        except:
            cmd_list = [instruction]
        for cmd in cmd_list:
            engine_reply = "= " + engine.send(cmd) + '\n\n'
            #print(engine_reply)
            # print(type(engine_reply))
            sys.stdout.write(engine_reply)
            sys.stdout.flush()
            over, winner = engine._game.is_game_over()
            '''if over:
                engine.disconnect = True
                p = '.XO'''
                #print(p[winner])
