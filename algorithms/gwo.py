import numpy as np


def gwo(obj_func, dim, lb, ub, N, MaxIter, seed=None):
    """
    Grey Wolf Optimizer (GWO)

    Parameters
    ----------
    obj_func : callable
        目标函数，输入 shape=(dim,) 的一维数组，返回一个标量 fitness。
    dim : int
        问题维度。
    lb : float or array-like
        下界。
    ub : float or array-like
        上界。
    N : int
        狼群规模。
    MaxIter : int
        最大迭代次数。
    seed : int or None
        随机种子，用于复现实验。

    Returns
    -------
    best_score : float
        最优 fitness。
    best_pos : ndarray
        最优位置。
    convergence_curve : ndarray
        每次迭代的当前最优 fitness。
    """

    # =========================================================
    # 1. 处理上下界
    # =========================================================
    lb = np.broadcast_to(np.asarray(lb, dtype=float), (dim,))
    ub = np.broadcast_to(np.asarray(ub, dtype=float), (dim,))

    # =========================================================
    # 2. 随机数生成器
    # =========================================================
    rng = np.random.default_rng(seed)

    # =========================================================
    # 3. 初始化狼群
    #    X.shape = (N, dim)
    # =========================================================
    X = rng.uniform(lb, ub, size=(N, dim))

    # =========================================================
    # 4. 初始化 alpha / beta / delta
    # =========================================================
    alpha_score = np.inf
    beta_score = np.inf
    delta_score = np.inf

    alpha_pos = np.zeros(dim)
    beta_pos = np.zeros(dim)
    delta_pos = np.zeros(dim)

    # =========================================================
    # 5. 收敛曲线
    # =========================================================
    convergence_curve = np.zeros(MaxIter)

    # =========================================================
    # 6. 主循环
    # =========================================================
    for t in range(MaxIter):

        # -----------------------------------------------------
        # 6.1 边界处理
        #     先确保当前种群全部位于搜索空间内，
        #     再计算 fitness。
        # -----------------------------------------------------
        X = np.clip(X, lb, ub)

        # -----------------------------------------------------
        # 6.2 计算所有狼的适应度
        # -----------------------------------------------------
        fitness = np.apply_along_axis(obj_func, 1, X)

        # -----------------------------------------------------
        # 6.3 更新 alpha / beta / delta
        # 按参考实现使用三个独立 if 顺序更新，便于论文代码复现。
        # -----------------------------------------------------
        for i in range(N):

            current_score = fitness[i]

            if current_score < alpha_score:
                alpha_score = current_score
                alpha_pos = X[i].copy()

            if current_score > alpha_score and current_score < beta_score:
                beta_score = current_score
                beta_pos = X[i].copy()

            if (
                    current_score > alpha_score
                    and current_score > beta_score
                    and current_score < delta_score
            ):
                delta_score = current_score
                delta_pos = X[i].copy()

        # -----------------------------------------------------
        # 6.4 a 从 2 线性下降到 0
        # -----------------------------------------------------
        a = 2.0 - 2.0 * t / MaxIter

        # -----------------------------------------------------
        # 6.5 更新每一只狼的位置
        # -----------------------------------------------------
        for i in range(N):

            # -----------------------------------------------------
            # 按原始 MATLAB 实现的随机数粒度：
            # 每个维度、每个领导者分别生成标量 r1 / r2
            # -----------------------------------------------------
            X1 = np.zeros(dim)
            X2 = np.zeros(dim)
            X3 = np.zeros(dim)

            for j in range(dim):

                # ===== alpha =====
                r1 = rng.random()
                r2 = rng.random()

                A1 = 2.0 * a * r1 - a
                C1 = 2.0 * r2

                D_alpha = abs(C1 * alpha_pos[j] - X[i, j])
                X1[j] = alpha_pos[j] - A1 * D_alpha

                # ===== beta =====
                r1 = rng.random()
                r2 = rng.random()

                A2 = 2.0 * a * r1 - a
                C2 = 2.0 * r2

                D_beta = abs(C2 * beta_pos[j] - X[i, j])
                X2[j] = beta_pos[j] - A2 * D_beta

                # ===== delta =====
                r1 = rng.random()
                r2 = rng.random()

                A3 = 2.0 * a * r1 - a
                C3 = 2.0 * r2

                D_delta = abs(C3 * delta_pos[j] - X[i, j])
                X3[j] = delta_pos[j] - A3 * D_delta

            # 三个领导者给出的结果取平均
            new_position = (X1 + X2 + X3) / 3.0

            # -------------------------------------------------
            # 边界处理
            # -------------------------------------------------
            X[i] = np.clip(new_position, lb, ub)

        # -----------------------------------------------------
        # 6.6 保存当前最优值
        # -----------------------------------------------------
        convergence_curve[t] = alpha_score

    # =========================================================
    # 7. 返回结果
    # =========================================================
    return alpha_score, alpha_pos, convergence_curve