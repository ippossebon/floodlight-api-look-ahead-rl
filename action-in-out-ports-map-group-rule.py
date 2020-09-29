def actionInOutPortMapToGroupRule(action):
    # 34 acoes possiveis

    if action == 0:
        # Switch 1
        # IN = 1, Out = 2
        return {
            "switch" : "00:00:00:00:00:00:00:01",
            "entry_type" : "group",
            "name" : "group-s1-in1-out2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "1",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=2"
                }
            ]
        }
    elif action == 1:
        # IN = 1, Out = 3
        return {
            "switch" : "00:00:00:00:00:00:00:01",
            "entry_type" : "group",
            "name" : "group-s1-in1-out3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "2",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=3"
                }
            ]
        }

    elif action == 2:
        # IN = 1, Out = 2,3
        return {
            "switch" : "00:00:00:00:00:00:00:01",
            "entry_type" : "group",
            "name" : "group-s1-in1-out2_3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "3",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions" : "output=3"
                }
            ]
        }

    elif action == 3:
        # Swiitch 2, IN 1, out 2
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in1-out2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "4",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 4:
        # Swiitch 2, IN 1, out 3
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in1-out3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "5",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=3"
                }
            ]
        }

    elif action == 5:
        # Swiitch 2, IN 1, out 4
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in1-out4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "6",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=4"
                }
            ]
        }

    elif action == 6:
        # Swiitch 2, IN 1, out 2,3
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in1-out2_3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "7",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions" : "output=3"
                }
            ]
        }

    elif action == 7:
        # Swiitch 2, IN 1, out 2,4
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in1-out2_4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "8",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions" : "output=4"
                }
            ]
        }

    elif action == 8:
        # Swiitch 2, IN 1, out 3,4
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in1-out3_4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "9",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=3"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions" : "output=4"
                }
            ]
        }

    elif action == 9:
        # Swiitch 2, IN 1, out 2,3,4
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in1-out2_3_4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "10",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "33",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "33",
                    "bucket_actions" : "output=3"
                },
                {
                    "bucket_id" : "3",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "34",
                    "bucket_actions" : "output=4"
                }
            ]
        }

    elif action == 10:
        # Swiitch 2, IN 2, out 3
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in2-out3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "11",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "2",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=3"
                }
            ]
        }

    elif action == 11:
        # Swiitch 2, IN 2, out 4
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in2-out4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "12",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "2",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=4"
                }
            ]
        }

    elif action == 12:
        # Swiitch 2, IN 2, out 3,4
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in2-out3_4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "13",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "2",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=3"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "2",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=4"
                }
            ]
        }

    elif action == 13:
        # Swiitch 4, IN 2, out 2
        return {
            "switch" : "00:00:00:00:00:00:00:04",
            "entry_type" : "group",
            "name" : "group-s4-in1-out2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "14",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 14:
        # Swiitch 4, IN 1, out 3
        return {
            "switch" : "00:00:00:00:00:00:00:04",
            "entry_type" : "group",
            "name" : "group-s4-in1-out3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "15",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=3"
                }
            ]
        }

    elif action == 15:
        # Swiitch 4, IN 1, out 2,3
        return {
            "switch" : "00:00:00:00:00:00:00:04",
            "entry_type" : "group",
            "name" : "group-s4-in1-out2_3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "16",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=3"
                }
            ]
        }

    elif action == 16:
        # Swiitch 3, IN 1, out 2
        return {
            "switch" : "00:00:00:00:00:00:00:03",
            "entry_type" : "group",
            "name" : "group-s3-in1-out2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "17",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 17:
        # Swiitch 3, IN 1, out 3
        return {
            "switch" : "00:00:00:00:00:00:00:03",
            "entry_type" : "group",
            "name" : "group-s3-in1-out3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "18",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=3"
                }
            ]
        }

    elif action == 18:
        # Swiitch 3, IN 1, out 4
        return {
            "switch" : "00:00:00:00:00:00:00:03",
            "entry_type" : "group",
            "name" : "group-s3-in1-out4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "19",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=4"
                }
            ]
        }

    elif action == 19:
        # Swiitch 3, IN 1, out 2,3
        return {
            "switch" : "00:00:00:00:00:00:00:03",
            "entry_type" : "group",
            "name" : "group-s3-in1-out2_3",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "20",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=3"
                }
            ]
        }

    elif action == 20:
        # Swiitch 3, IN 1, out 2,4
        return {
            "switch" : "00:00:00:00:00:00:00:03",
            "entry_type" : "group",
            "name" : "group-s3-in1-out2_4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "21",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=4"
                }
            ]
        }

    elif action == 21:
        # Swiitch 3, IN 1, out 3,4
        return {
            "switch" : "00:00:00:00:00:00:00:03",
            "entry_type" : "group",
            "name" : "group-s3-in1-out3_4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "22",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=3"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=4"
                }
            ]
        }

    elif action == 22:
        # Swiitch 3, IN 1, out 2,3,4
        return {
            "switch" : "00:00:00:00:00:00:00:03",
            "entry_type" : "group",
            "name" : "group-s3-in1-out2_3_4",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "23",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "33",
                    "bucket_actions":"output=2"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "33",
                    "bucket_actions":"output=3"
                },
                {
                    "bucket_id" : "3",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "1",
                    "bucket_weight" : "34",
                    "bucket_actions":"output=4"
                }
            ]
        }

    elif action == 23:
        # Swiitch 2, IN 4, out 1
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in4-out1",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "24",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "4",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=1"
                }
            ]
        }

    elif action == 24:
        # Swiitch 2, IN 4, out 2
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in4-out2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "25",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "4",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 25:
        # Swiitch 2, IN 4, out 1,2
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in4-out1_2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "26",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "4",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=1"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "4",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 26:
        # Swiitch 2, IN 3, out 1
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in3-out1",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "27",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=1"
                }
            ]
        }

    elif action == 27:
        # Swiitch 2, IN 3, out 2
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in3-out2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "28",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 28:
        # Swiitch 2, IN 3, out 1,2
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in3-out1_2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "29",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=1"
                },
                {
                    "bucket_id" : "2",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 29:
        # Swiitch 2, IN 2, out 1
        return {
            "switch" : "00:00:00:00:00:00:00:02",
            "entry_type" : "group",
            "name" : "group-s2-in2-out1",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "30",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "2",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=1"
                }
            ]
        }

    elif action == 30:
        # Swiitch 4, IN 3, out 1
        return {
            "switch" : "00:00:00:00:00:00:00:04",
            "entry_type" : "group",
            "name" : "group-s4-in3-out1",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "31",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=1"
                }
            ]
        }

    elif action == 31:
        # Swiitch 4, IN 3, out 2
        return {
            "switch" : "00:00:00:00:00:00:00:04",
            "entry_type" : "group",
            "name" : "group-s4-in3-out2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "32",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 32:
        # Swiitch 4, IN 3, out 1,2
        return {
            "switch" : "00:00:00:00:00:00:00:04",
            "entry_type" : "group",
            "name" : "group-s4-in3-out1_2",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "33",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=1"
                },
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "3",
                    "bucket_weight" : "50",
                    "bucket_actions":"output=2"
                }
            ]
        }

    elif action == 33:
        # Swiitch 4, IN 2, out 1
        return {
            "switch" : "00:00:00:00:00:00:00:04",
            "entry_type" : "group",
            "name" : "group-s4-in2-out1",
            "active" : "true",
            "group_type" : "select",
            "group_id" : "34",
            "group_buckets" : [
                {
                    "bucket_id" : "1",
                    "bucket_watch_group" : "any",
                    "bucket_watch_port" : "2",
                    "bucket_weight" : "100",
                    "bucket_actions":"output=1"
                }
            ]
        }
