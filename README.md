# 介绍

这是AlphaGo Zero的复现和修改版本。修改包括用Path consistency及其变种Feature matching来加速训练。本项目既可自我对弈生成训练数据，
本项目可在围棋和Hex间切换。

# 文件说明

* main.py 训练模型的主程序
* selfplay.py 自我对弈的程序
* pc.py 用path consistency进行自我对弈的程序
* fm.py 用feature matching训练模型的主程序
* network.py 模型所用的神经网络
* mcts.py 蒙特卡洛树搜索
* play.py 与程序进行对弈
* hex.py Hex棋的规则
* go.py 围棋的规则
* 2conquer.py dataset.py 制作、处理数据集
* *.model 保存的模型
* mse.txt ce.txt acc.txt err.txt 保存的loss、准确率

# 依赖

* Ubuntu 14.04+
* Python 3.6+
* Pytorch 0.4.0+
* numpy
* pysgf
* 至少一块Nvidia显卡

# 运行

```
# 执行自我对弈（若要使用path consistency，则要将selfplay.py改为pc.py）
./run.sh

# 仅用监督学习从0开始训练模型
python main.py

# 仅用监督学习从current.model开始训练模型
python main.py --saved_model=current.model

# 与current.model进行对弈
python play.py --saved_model=current.model
```

# 相关链接

* AlphaGo https://storage.googleapis.com/deepmind-media/alphago/AlphaGoNaturePaper.pdf
* AlphaGo Zero https://deepmind.com/documents/119/agz_unformatted_nature.pdf
