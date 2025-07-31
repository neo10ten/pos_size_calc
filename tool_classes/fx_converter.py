



class ForexConverter:
    @staticmethod
    def get_rate(b, q):
        return fetch_rate(b, q)