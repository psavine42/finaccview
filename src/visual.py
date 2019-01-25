import numpy as np
from .discrete import dvc_base as dvc


notes = \
    """
    Let P := {p 1 , ...., p n } be a set of n distinct points in R 2 
        with the coordinates (x 1 , y 1 ), ..., (x n , y n ). 
        These points are the generators. 
    
    The subdivision of R 2 into n Voronoi regions V (p_i), 
        with the property that a point q(x, y) lies in the region V (p i ) 
            if and only if distance(p_i , q) < distance(p j , q) 
            for each p i , p j ∈ P with i 6 = j, is defined as the Voronoi tessellation
    V (P) := {V (p 1 ), ...,V (p n )}. 
    
    The denotation distance(p i , q) represents a specified distance function between the generator p i and
    the point q. 
    In general, a Voronoi tessellation is defined in an unbounded space. 
    Having a bounded space S, the set V ∩S (P) := {V (p 1 ) ∩ S, ...,V (p n ) ∩ S} 
    is called a bounded Voronoi tessellation
    """


def euclidean_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 - (p1[1] - p2[1]) ** 2) ** 0.5


def distance_pw(generator_point, weight, point):
    return euclidean_distance(generator_point, point) ** 2 - weight


def distance_aw(generator_point, weight, point):
    return euclidean_distance(generator_point, point) - weight


# -----------------------------------------
def _adjust_weights_aw(w_i, a_i, a_desired):
    return


def _adjust_weights_pw(w_i, a_i, a_desired):
    assert a_desired != 0
    w_i = w_i * (1 + (a_desired - a_i) / a_desired)
    if w_i < 1:
        w_i = 1
    return w_i


def adjust_weights(weights, area, desired, add=True):
    if add is True:
        return _adjust_weights_aw(weights, area, desired)
    else:
        return _adjust_weights_pw(weights, area, desired)


# -----------------------------------------
def move_generators(points, weights, voronoi):
    """
    Algorithm 4 MoveGenerators() for AW Voronoi Treemaps

    Input: set of n points P := {p 1 , ..., p n }; set of n weights W :=
        {w 1 , ..., w n }; AW Voronoi tessellation V aw∩S (P,W )

    Output:
        set of n points P := {p 1 , ..., p n } with p i =
            CenterO f Mass(V aw (p i , w i )) and V aw (p i , w i ) ∈ V aw∩S (P,W );
        set of n weights W := {w 1 , ..., w n }
            with kp i − p j k 2 − (w i + w j ) ≥ 0 for {p i , p j } ⊂ P, i 6 = j

    for each p i ∈ P do
        p_i = Center Of Mass( Vaw (p i , w i )) e V aw∩S ( P,W )

    f actorWeight = ∞
    for each {p i , p j } ⊂ P with i != j do
        f = w i i +w j j
        if 0 < f < f actorWeight then
            f actorWeight = f

    if f actorWeight < 1 then
        for each w i ∈ W do
            w_i = w_i · f actorWeight
    """
    for i in range(len(points)):
        points[i] = voronoi[i].center_of_mass

    factor_weight = float('inf')
    for i in range(points):
        for j in range(i+1, points):
            f = (points[i] - points[j]) ** 2 / (weights[i] + weights[j])
            if 0 < f < factor_weight:
                factor_weight = f
    if factor_weight < 1:
        for w in weights:
            w *= factor_weight
    return points, weights


def extract_subareas(voronoi):
    for site in voronoi._cells:
        # site.
        return
    return voronoi


def voronoi_treemap_subdiv(plane, points, desired_areas, epsilon=5, add=False):
    """
    Algorithm 1: Voronoi Treemap subdivision

    Input:
        bounded plane S in R^2 ;
        set of n values A desired :=
            {{a_1_desired , ..., a_n_desired } : 0 < a_i_desired ≤ 1 , ∑ a_i_desired = 1};
        error threshold ε

    Output:
        subdivision of 'S' in 'n' disjoint subareas s_i ⊂ S with
         AreaSize(s_i) / (AreaSize(S) − a_i_desired) < ε

    initialize a set of n points P := {p 1 , ..., p n } with p i ∈ S, p i 6 = p j
    initialize a set of n weights W := {w 1 , ..., w n } with w i = 1
    initialize a data structure for the Voronoi tessellation V ∩S (P,W )

    while stable == False
        ComputeVoronoiTessellation(V ∩S (P,W ))
        stable = true
        initialize a set of n values A := {a 1 , ..., a n }
        for each a i ∈ A do
            a_i = (AreaSize(V (p i ,w i )))/ AreaSize(S) with Voronoi region V (p i , w i ) ∈

            V ∩ S (P,W )
            if | a_i − a_desired | ≥ ε then
                stable = False

        for each w i ∈ W do
            AdjustWeight(w_i , a_i , a_i_desired )

        MoveGenerators(P, W, V_∩S(P,W ))

    ExtractSubareas(V_∩S (P,W ))
    """
    weights = [1] * len(desired_areas)     # W
    voronoi = dvc.VoronoiDBC(points=points, space=plane)     # V
    stable = False

    while stable is False:
        voronoi.create_voronoi()
        stable = True
        areas = list(range(len(points)))
        for i, a_i in enumerate(areas):
            a_i = voronoi[i].area / plane.area
            if abs(a_i - desired_areas[i]) > epsilon:
                stable = False

        for i, w in enumerate(weights):
            # adjust the wieghts
            weights[i] = adjust_weights(
                w, areas[i], desired_areas[i], add=add
            )

        points, weights = move_generators(points, weights, voronoi)

    return voronoi


