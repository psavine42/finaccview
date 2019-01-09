
def voronoi_treemap():
    """
    Algorithm 1: Voronoi Treemap subdivision

    Input:
        bounded plane S in R^2 ;
        set of n values A desired :=
            {a 1 desired , ..., a_n_desired } with 0 < a_i_desired ≤ 1 and ∑ a_i_desired = 1;
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
            AdjustWeight(w i , a i , a i desired )

        MoveGenerators(P, W, V_∩S(P,W ))

    ExtractSubareas(V_∩S (P,W ))
    """
    stable = False

