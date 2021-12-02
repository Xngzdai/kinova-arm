"""
procrusteanfilter.jl
"""

struct ProcrusteanFilterState
    Name::String
end

struct ProcrusteanFilter
    V::AbstractVector{String} #State Space
    V0::AbstractVector{String} #Initial States
    Y::AbstractVector{String} #Observations
    Transitions::AbstractVector{AbstractMatrix{Int}}
    C::AbstractVector{String}
    c::AbstractVector{AbstractVector{String}}
    # Additional Inputs
end

"""
GetProcrusteanFilter
Description:

"""
function GetProcrusteanFilter( names::AbstractVector{String} , initialNames::AbstractVector{String} )
    # Constants

    # Algorithm

end

"""
state_name_to_index
Description:

"""
function state_name_to_index( pf::ProcrusteanFilter , q::String )
    # Constants
    num_states = length(pf.V)

    # Algorithm
    for v_index in 1:num_states
        temp_v = pf.V[v_index]
        if temp_v == q
            return v_index
        end
    end

    # If this state wasn't found, then return -1.
    return -1
        
end

function observation_name_to_index(pf::ProcrusteanFilter, y_name::String)
    #Constants
    num_obs = length(pf.Y)

    #Algorithm
    for y_index in 1:num_obs
        temp_y = pf.Y[y_index]
        if temp_y == y_name
            return y_index
        end
    end

    # If y_name is not in the space Y, then return -1.
    return -1
end

"""
Post
Description:
    Determines the states which succeed the current state or the current state-observation pair 
    in the Procrustean Filter.
"""
function Post( pf::ProcrusteanFilter , v::String , y::String )
    # Constants
    v_index = state_name_to_index(pf,v)
    y_index = observation_name_to_index(pf,y)

    # Algorithm
    next_states = []

    # Look through all rows of the transition matrix for v_index
    temp_trans_matrix = pf.Transitions[v_index]
    for row_index in 1:size(temp_trans_matrix,1)
        temp_row = temp_trans_matrix[row_index,:]
        if temp_row[y_index] == 1
            append!(next_states,[pf.V[row_index]])
        end
    end

    return next_states

end

function Post( pf::ProcrusteanFilter , v::String )
    # Constants

    # Algorithm
    next_states = []

    # Look through all rows of the transition matrix for v_index
    for temp_y in pf.Y
        append!(next_states,Post(pf,v,temp_y))
    end

    return unique(next_states)

end

"""
add_transition
Description:
    Adds a transition to the Procrustean Filter.
    Throws an error if some states do not exist yet.
"""
function add_transition!(pf::ProcrusteanFilter,v_i::String,y_i::String,v_ip1::String)
    # Constants
    v_i_index = state_name_to_index(v_i)
    y_i_index = observation_name_to_index(y_i)
    v_ip1_index = state_name_to_index(v_ip1)

    # Input Checking
    if v_i_index == -1
        throw("The state %s does not exist in the procrustean filter.",v_i)

    if y_i_index == -1
        throw("The observation %s does not exist in the procrustean filter.",y_i)

    if v_ip1_index == -1
        throw("The state %s does not exist in the procrustean filter.",v_ip1)

    # Algorithm
    pf.Transitions[v_i_index][v_ip1_index,y_i_index] = 1

end