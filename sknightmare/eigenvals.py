import csv
import numpy as np

rows = []

with open("covariance.csv","r") as infile:
    reader = csv.reader(infile)
    for i,row in enumerate(reader):
        newr = (list(map(float,row)))
        for j,n in enumerate(newr):
            if j != i:
                newr[j] = n/5.0
            else:
                newr[j] = 0.05
        rows.append(newr)

mat = np.matrix(rows)
print(mat.shape)
print(mat)
print(np.linalg.eigvals(mat))
print(np.all(np.linalg.eigvals(mat)>0))

lambdas, V =  np.linalg.eig(mat)
print(V)
print(mat[lambdas == 0,:])

# with open("fixedcovariance.csv","w+") as outfile:
#     writer = csv.writer(outfile)
#     for row in mat:
#         writer.writerow(row)
np.savetxt("fixedcovariance.csv",mat)