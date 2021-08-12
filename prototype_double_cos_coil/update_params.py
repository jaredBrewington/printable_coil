import numpy as np

def set_params():
    numOfCoils = 1
    innerRadius = 0.035
    outerRadius = 0.035 + 0.01

    coilX = 0.225
    coilY = 0
    coilZ = 0
    coilPos = [coilX, coilY, coilZ]

    length1 = 0.30
    # length2 = .15
    # length3 = .25
    # length4 = .25
    # length5 = .75
    # lengthCoils = [length1, length2, length3, length4, length5]
    lengthCoils = [length1]
    coilGap = .00025

    parameters = [numOfCoils, outerRadius, innerRadius] + coilPos + lengthCoils + [coilGap]

    print(parameters)

    with open('parameters.txt','w') as f:
        for x in parameters[:-1]:
            f.write('%f\n' %x)
        f.write(str(parameters[-1]))

def main():
    set_params()



if __name__ == '__main__':
    main()