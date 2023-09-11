import facebook


class Facebook:
    """
    Facebook class to fetch the user info and return it
    """

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the facebook GraphAPI to fetch the user info
        """
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            # profile = graph.request('/me?fields=name,email')

            profile = graph.get_object("me")
            args = {
                "fields": "id,name,email,picture.type(large),first_name,last_name,gender,birthday,hometown,location,education,work",
            }
            profile = graph.get_object("me", **args)
            # print(profile)
            return profile
        except:
            return "The token is invalid or expired."
