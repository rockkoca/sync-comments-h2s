/**
 * @file test_sh2s.h
 * @version 1.0
 *
 * This is a test file.
 *
 * All the comments in this file will be synced to
 * corresponding source files(same file name except the extension).
 *
 *
 */

#include "test_sh2s.h"
const CONST_VALUE = 1;

/**
 * Test_sh2s
 * Test comments for constructor
 *
 */
// test in line comment for constructor
Test_sh2s::Test_sh2s() {

}

/**
 * Test_sh2s
 *
 * @param num : int number
 * @param age : age
 */
Test_sh2s::Test_sh2s(int num, int age) {

}

/**
 * doSomething1
 */
void Test_sh2s::doSomething1() {

}

/**
 * doSomething1
 *
 * over load test
 * @param overload
 */
void Test_sh2s::doSomething1(int overload) {

}

// doSomething2
int Test_sh2s::doSomething2() {
   return 0;
}

/**
 * complexArgs
 * @param arg1
 * @param arg2
 * @param arg3
 * @param arg4
 * @param arg5
 *
 * Test_sh2s::Node is required.
 * If only use Node here, this program cannot find the function in
 * source file.
 *
 * It does not analyze such relationships.
 */
void Test_sh2s::complexArgs(int arg1, int arg2, char arg3, int *arg4, int *&arg5, Test_sh2s::Node *left) {

}

/**
 * doSomething3
 * @return
 */
Test_sh2s::Node *Test_sh2s::doSomething3() {
   return nullptr;
}

/**
 * doSomething4
 * @return
 */
Test_sh2s::Node &Test_sh2s::doSomething4() {
   return <#initializer#>;
}

/**
 * doSomething1Helpers
 * @param head
 */
void Test_sh2s::doSomething1Helpers(Test_sh2s::Node *head) {

}

// constructor of Node
Test_sh2s::Node::Node(int val, Test_sh2s::Node *left, Test_sh2s::Node *right) {

}

/**
 * test_c_func
 * Test c function
 */
void test_c_func(int test){

}
