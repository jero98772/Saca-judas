import numpy as np

def jacobi(A: list, b: list, tolerance: float, x_0: list, decimals: int = 6):
     A = np.array(A, dtype=float)
     b = np.array(b, dtype=float)
     n = len(b)
     logs = []

     if A.shape[0] != A.shape[1]:
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.tolist(),
                "b": b.tolist(),
                "message": f"Matrix A must be square. Received {A.shape[0]}x{A.shape[1]}."
            }]
        }

     if A.shape[0] != len(b):
        return {
            "solution": None,
            "logs": [{
                "step": "Check",
                "A": A.tolist(),
                "b": b.tolist(),
                "message": f"The size of vector b ({len(b)}) does not match the number of rows in A ({A.shape[0]})."
            }]
        }
     
     n = len(b)
     eigen_val = np.linalg.eig(A)
     espectral_rate = max(eigen_val)


def diagonally_dominant(A):
     if A.shape[0] != A.shape[1]:
          return {
               "message": ""
          }
          

     

