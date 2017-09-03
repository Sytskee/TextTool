from sklearn.feature_selection import SelectKBest

class SelectAtMostKBest(SelectKBest):
    def _check_params(self, X, y):
        if not (self.k == 'all' or 0 <= self.k <= X.shape[1]):
            #print("Requested more features (%d) then available (%d)" % (self.k, X.shape[1]))
            # Set k to "all" (skip feature selection), if less than k features are available
            self.k = 'all'
        # elif not self.k == 'all':
        #     print("Requested %d features, %d available" % (self.k, X.shape[1]))