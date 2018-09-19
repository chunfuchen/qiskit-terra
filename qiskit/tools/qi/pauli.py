# -*- coding: utf-8 -*-

# Copyright 2017, IBM.
#
# This source code is licensed under the Apache License, Version 2.0 found in
# the LICENSE.txt file in the root directory of this source tree.

# pylint: disable=invalid-name

"""
Tools for working with Pauli Operators.

A simple pauli class and some tools.
"""
import random

import numpy as np
from scipy import sparse


class Pauli:
    """A simple class representing Pauli Operators.

    The form is P = (-i)^dot(v,w) Z^v X^w where v and w are elements of Z_2^n.
    That is, there are 4^n elements (no phases in this group).

    For example, for 1 qubit
    P_00 = Z^0 X^0 = I
    P_01 = X
    P_10 = Z
    P_11 = -iZX = (-i) iY = Y

    Multiplication is P1*P2 = (-i)^dot(v1+v2,w1+w2) Z^(v1+v2) X^(w1+w2)
    where the sums are taken modulo 2.

    Pauli vectors v and w are supposed to be defined as numpy arrays.

    Ref.
    Jeroen Dehaene and Bart De Moor
    Clifford group, stabilizer states, and linear and quadratic operations
    over GF(2)
    Phys. Rev. A 68, 042318 – Published 20 October 2003
    """

    def __init__(self, v, w):
        """Make the Pauli class."""
        self.numberofqubits = len(v)
        self.v = v
        self.w = w

    def __str__(self):
        """Output the Pauli as first row v and second row w."""
        stemp = 'v = '
        for i in self.v:
            stemp += str(i) + '\t'
        stemp = stemp + '\nw = '
        for j in self.w:
            stemp += str(j) + '\t'
        return stemp

    def __eq__(self, other):
        """Return True if all Pauli terms are equal."""
        bres = False
        if self.numberofqubits == other.numberofqubits:
            if np.all(self.v == other.v) and np.all(self.w == other.w):
                bres = True
        return bres

    def __mul__(self, other):
        """Multiply two Paulis."""
        if self.numberofqubits != other.numberofqubits:
            print('These Paulis cannot be multiplied - different number '
                  'of qubits')
        v_new = (self.v + other.v) % 2
        w_new = (self.w + other.w) % 2
        pauli_new = Pauli(v_new, w_new)
        return pauli_new

    def to_label(self):
        """Print out the labels in X, Y, Z format.

        Returns:
            str: pauli label
        """
        p_label = ''
        for j_index in range(self.numberofqubits):
            if self.v[j_index] == 0 and self.w[j_index] == 0:
                p_label += 'I'
            elif self.v[j_index] == 0 and self.w[j_index] == 1:
                p_label += 'X'
            elif self.v[j_index] == 1 and self.w[j_index] == 1:
                p_label += 'Y'
            elif self.v[j_index] == 1 and self.w[j_index] == 0:
                p_label += 'Z'
        return p_label

    def to_matrix(self):
        """Convert Pauli to a matrix representation.

        Order is q_n x q_{n-1} .... q_0

        Returns:
            numpy.array: a matrix that represnets the pauli.
        """
        x = np.array([[0, 1], [1, 0]], dtype=complex)
        y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        z = np.array([[1, 0], [0, -1]], dtype=complex)
        id_ = np.array([[1, 0], [0, 1]], dtype=complex)
        matrix = 1
        for k in range(self.numberofqubits):
            if self.v[k] == 0 and self.w[k] == 0:
                new = id_
            elif self.v[k] == 1 and self.w[k] == 0:
                new = z
            elif self.v[k] == 0 and self.w[k] == 1:
                new = x
            elif self.v[k] == 1 and self.w[k] == 1:
                new = y
            else:
                print('the string is not of the form 0 and 1')
            matrix = np.kron(new, matrix)

        return matrix

    def to_spmatrix(self):
        """Convert Pauli to a sparse matrix representation (CSR format).

        Order is q_n x q_{n-1} .... q_0

        Returns:
            scipy.sparse.csr_matrix: a sparse matrix with CSR format that
            represnets the pauli.
        """
        matrix = sparse.coo_matrix(np.array([[1]], dtype=complex))
        for k in range(self.numberofqubits):
            if self.v[k] == 0 and self.w[k] == 0:
                temp = [[matrix, None], [None, matrix]]
            elif self.v[k] == 1 and self.w[k] == 0:
                temp = [[matrix, None], [None, -matrix]]
            elif self.v[k] == 0 and self.w[k] == 1:
                temp = [[None, matrix], [matrix, None]]
            elif self.v[k] == 1 and self.w[k] == 1:
                temp = [[None, matrix * -1j], [matrix * 1j, None]]
            matrix = sparse.bmat(temp, "coo")

        return matrix.tocsr()


def random_pauli(number_qubits):
    """Return a random Pauli on numberofqubits."""
    v = np.array(list(bin(random.getrandbits(number_qubits))
                      [2:].zfill(number_qubits))).astype(np.int)
    w = np.array(list(bin(random.getrandbits(number_qubits))
                      [2:].zfill(number_qubits))).astype(np.int)
    return Pauli(v, w)


def sgn_prod_old(P1, P2):
    """Multiply two Paulis P1*P2 and track the sign.

    P3 = P1*P2: X*Y
    """

    if P1.numberofqubits != P2.numberofqubits:
        print('Paulis cannot be multiplied - different number of qubits')
    v_new = (P1.v + P2.v) % 2
    w_new = (P1.w + P2.w) % 2
    paulinew = Pauli(v_new, w_new)
    phase = 1
    for i in range(len(P1.v)):
        if P1.v[i] == 1 and P1.w[i] == 0 and P2.v[i] == 0 and P2.w[i] == 1:
            # Z*X
            phase = 1j * phase
        elif P1.v[i] == 0 and P1.w[i] == 1 and P2.v[i] == 1 and P2.w[i] == 0:
            # X*Z
            phase = -1j * phase
        elif P1.v[i] == 0 and P1.w[i] == 1 and P2.v[i] == 1 and P2.w[i] == 1:
            # X*Y
            phase = 1j * phase
        elif P1.v[i] == 1 and P1.w[i] == 1 and P2.v[i] == 0 and P2.w[i] == 1:
            # Y*X
            phase = -1j * phase
        elif P1.v[i] == 1 and P1.w[i] == 1 and P2.v[i] == 1 and P2.w[i] == 0:
            # Y*Z
            phase = 1j * phase
        elif P1.v[i] == 1 and P1.w[i] == 0 and P2.v[i] == 1 and P2.w[i] == 1:
            # Z*Y
            phase = -1j * phase

    return paulinew, phase


def sgn_prod(P1, P2):
    """Multiply two Paulis P1*P2 and track the sign.

    P3 = P1*P2: X*Y
    """

    if P1.numberofqubits != P2.numberofqubits:
        print('Paulis cannot be multiplied - different number of qubits')

    p1_v = P1.v.astype(np.bool)
    p1_w = P1.w.astype(np.bool)
    p2_v = P2.v.astype(np.bool)
    p2_w = P2.w.astype(np.bool)

    v_new = np.logical_xor(p1_v, p2_v).astype(np.int)
    w_new = np.logical_xor(p1_w, p2_w).astype(np.int)

    paulinew = Pauli(v_new, w_new)
    phase = 0  # 1

    for v1, w1, v2, w2 in zip(p1_v, p1_w, p2_v, p2_w):
        if v1 and not w1:  # Z
            if w2:
                phase = phase - 1 if v2 else phase + 1
        elif not v1 and w1:  # X
            if v2:
                phase = phase + 1 if w2 else phase - 1
        elif v1 and w1:  # Y
            if not v2 and w2:  # X
                phase -= 1  # -1j * phase
            elif v2 and not w2:  # Z
                phase += 1  # 1j * phase

    # for i in range(len(p1_v)):
    #     if p1_v[i] and not p1_w[i]:  # Z
    #         if p2_w[i]:
    #             if p2_v[i]:  # Y
    #                 phase -= 1  # -1j * phase
    #             else:  # X
    #                 phase += 1  # 1j * phase
    #     elif not p1_v[i] and p1_w[i]:  # X
    #         if p2_v[i]:
    #             if p2_w[i]:  # Y
    #                 phase += 1  # 1j * phase
    #             else:  # Z
    #                 phase -= 1  # -1j * phase
    #     elif p1_v[i] and p1_w[i]:  # Y
    #         if not p2_v[i] and p2_w[i]:  # X
    #             phase -= 1  #  -1j * phase
    #         elif p2_v[i] and not p2_w[i]:  # Z
    #             phase += 1  # 1j * phase

    phase = (1j) ** (phase % 4)
    return paulinew, phase


def inverse_pauli(other):
    """Return the inverse of a Pauli."""
    v = other.v
    w = other.w
    return Pauli(v, w)


def label_to_pauli(label):
    """Return the pauli of a string ."""
    v = np.zeros(len(label))
    w = np.zeros(len(label))
    for j, _ in enumerate(label):
        if label[j] == 'I':
            v[j] = 0
            w[j] = 0
        elif label[j] == 'Z':
            v[j] = 1
            w[j] = 0
        elif label[j] == 'Y':
            v[j] = 1
            w[j] = 1
        elif label[j] == 'X':
            v[j] = 0
            w[j] = 1
        else:
            print('something went wrong')
            return -1
    return Pauli(v, w)


def pauli_group(number_of_qubits, case=0):
    """Return the Pauli group with 4^n elements.

    The phases have been removed.
    case 0 is ordered by Pauli weights and
    case 1 is ordered by I,X,Y,Z counting last qubit fastest.

    Args:
        number_of_qubits (int): number of qubits
        case (int): determines ordering of group elements (0=weight, 1=tensor)

    Returns:
        list: list of Pauli objects

    Note:
        WARNING THIS IS EXPONENTIAL
    """
    if number_of_qubits < 5:
        temp_set = []
        if case == 0:
            tmp = pauli_group(number_of_qubits, case=1)
            # sort on the weight of the Pauli operator
            return sorted(tmp, key=lambda x: -np.count_nonzero(
                np.array(x.to_label(), 'c') == b'I'))

        elif case == 1:
            # the Pauli set is in tensor order II IX IY IZ XI ...
            for k_index in range(4 ** number_of_qubits):
                v = np.zeros(number_of_qubits)
                w = np.zeros(number_of_qubits)
                # looping over all the qubits
                for j_index in range(number_of_qubits):
                    # making the Pauli for each kindex i fill it in from the
                    # end first
                    element = int((k_index) / (4 ** (j_index))) % 4
                    if element == 0:
                        v[j_index] = 0
                        w[j_index] = 0
                    elif element == 1:
                        v[j_index] = 0
                        w[j_index] = 1
                    elif element == 2:
                        v[j_index] = 1
                        w[j_index] = 1
                    elif element == 3:
                        v[j_index] = 1
                        w[j_index] = 0
                temp_set.append(Pauli(v, w))
            return temp_set

    print('please set the number of qubits to less than 5')
    return -1


def pauli_singles(j_index, number_qubits):
    """Return the single qubit pauli in number_qubits."""
    # looping over all the qubits
    tempset = []
    v = np.zeros(number_qubits)
    w = np.zeros(number_qubits)
    v[j_index] = 0
    w[j_index] = 1
    tempset.append(Pauli(v, w))
    v = np.zeros(number_qubits)
    w = np.zeros(number_qubits)
    v[j_index] = 1
    w[j_index] = 1
    tempset.append(Pauli(v, w))
    v = np.zeros(number_qubits)
    w = np.zeros(number_qubits)
    v[j_index] = 1
    w[j_index] = 0
    tempset.append(Pauli(v, w))
    return tempset
