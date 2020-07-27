def linksToPaths(links):
    path_c_g_i = ['a', 'c', 'g', 'i']
    path_b_f_i = ['a', 'b', 'f', 'i']
    path_b_d_h_i = ['a', 'b', 'd', 'h', 'i']
    path_b_e_g_i = ['a', 'b', 'e', 'g', 'i']
    path_c_e_f_i = ['a', 'c', 'e', 'f', 'i']
    path_c_e_d_h_i = ['a', 'c', 'e', 'd', 'h', 'i']

    action_0 = []
    action_1 = path_c_g_i + path_b_f_i
    action_2 = path_b_d_h_i + path_b_e_g_i
    action_3 = path_b_f_i
    action_4 = path_c_g_i + path_c_e_f_i
    action_5 = path_c_g_i
    action_6 = path_b_d_h_i
    action_7 = path_b_e_g_i
    action_8 = path_c_e_d_h_i
    action_9 = path_c_e_f_i
    action_10 = path_b_d_h_i + path_b_e_g_i + path_b_f_i

    links_set = set(links)

    if links_set == set(action_0):
        return []
    if links_set == set(action_1):
        return [path_c_g_i, path_b_f_i]
    if links_set == set(action_2):
        return [path_b_d_h_i, path_b_e_g_i]
    if links_set == set(action_3):
        return [path_b_f_i]
    if links_set == set(action_4):
        return [path_c_g_i, path_c_e_f_i]
    if links_set == set(action_5):
        return [path_c_g_i]
    if links_set == set(action_6):
        return [path_b_d_h_i]
    if links_set == set(action_7):
        return [path_b_e_g_i]
    if links_set == set(action_8):
        return [path_c_e_d_h_i]
    if links_set == set(action_9):
        return [path_c_e_f_i]
    if links_set == set(action_10):
        return [path_b_d_h_i, path_b_e_g_i, path_b_f_i]
    else:
        return None
