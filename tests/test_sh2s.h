/**
 * ＠file test_sh2s.h
 * @version 1.0
 *
 * This is a test file.
 *
 * All the comments in this file will be synced to
 * corresponding source files(same file name except the extension).
 *
 *
 */

#ifndef TEST_SH2S_H
#define TEST_SH2S_H


#include "transaction.h"


class Test_sh2s {

public:
   /**
    * Test_sh2s
    * Test comments for constructor
    *
    */
   // test in line comment for constructor
   Test_sh2s();

   /**
    * Test_sh2s
    *
    * @param num : int number
    * @param age : age
    */
   Test_sh2s(int num = 1, int age);

   /**
    * doSomething1
    */
   void doSomething1();

   /**
    * doSomething1
    *
    * over load test
    * @param overload
    */
   void doSomething1(int overload);

   // doSomething2
   int doSomething2();

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
   void complexArgs(int arg1, int arg2, char arg3 = 'c', int *arg4,
                    int *&arg5, Test_sh2s::Node *left);

   /**
    * doSomething3
    * @return
    */
   Test_sh2s::Node *doSomething3();

   /**
    * doSomething4
    * @return
    */
   Test_sh2s::Node &doSomething4();

private:
   struct Node {
      int val;
      Node *left;
      Node *right;

      // constructor of Node
      Node(int val, Test_sh2s::Node *left = nullptr, Test_sh2s::Node *right = nullptr);

   };

   /**
    * doSomething1Helpers
    * @param head
    */
   void doSomething1Helpers(Test_sh2s::Node *head);


};


#endif //TEST_SH2S_H
