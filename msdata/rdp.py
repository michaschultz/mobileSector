import numpy as np



@staticmethod
def simplify(points, tolerance, anchors):
	sqTolerance = tolerance * tolerance
	# !!! ATTENTION python list starts with [] not as JAVA list with () !!!
	pos = [0]

	anchors.sort()
	for i in range(1, len(anchors)):
		first = anchors[i-1]
		last  = anchors[i]
		simplifyDPStep(points, first, last, sqTolerance, pos)
		pos.append(last)
    
	anchors.clear()
	anchors.extend(pos)


# 	static void simplifyDPStep(float[][] points, int first, int last, float sqTolerance, ArrayList<Integer> pos)
def simplifyDPStep(points, first, last, sqTolerance, pos):
	maxSqDist = sqTolerance
	index = 0

	for i in range(first+1, last):
		sqDist = getSqSegDist(points[i], points[first], points[last])
		if sqDist > maxSqDist:
			index = i
			maxSqDist = sqDist
	
	if maxSqDist > sqTolerance:
		if (index - first) > 1:
			simplifyDPStep(points, first, index, sqTolerance, pos)

		pos.append(index)

		if (last - index) > 1:
			simplifyDPStep(points, index, last, sqTolerance, pos)


# static float getSqSegDist(float[] p, float[] p1, float[] p2)
def getSqSegDist(p, p1, p2):
	dim = len(p1)
	r = p1.copy()

	if not isSamePoint(p1,p2):
		t = 0

		for i in range(dim):
			t += (p[i] - r[i]) * (p2[i] - p1[i])

		t /= getSqDist(p1, p2)

		if t > 1:
			for i in range(dim):
				r[i]  = p2[i]
		elif t > 0:
			for i in range(dim):
				r[i] += (p2[i] - p1[i]) * t

	return getSqDist(p, r)



# static float getSqDist(float[] p1, float[] p2) {
def getSqDist(p1, p2):
	dd = 0
	for i in range(len(p1)):
		d = p1[i] - p2[i]
		dd += d*d
	return dd


def isSamePoint(fPoint1 , fPoint2):
	return np.array_equal(fPoint1, fPoint2)



def test():
    pos = np.array([
    [1,1], 
        [2,2],
        [3,3],
        [7,27],
        [10,10]
        ])

    print(pos[1][0])
    print(pos[1][1])

    anchors = [0, 1, len(pos)-1]
    print(anchors)

    simplify(pos, 1.8, anchors)

    print(anchors)