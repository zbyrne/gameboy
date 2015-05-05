#ifndef TEST_ME
#define TEST_ME

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct ErrMsgList{
    struct ErrMsgList *next;
    char *msg;
};

#define TESTME_START(name) \
    uint8_t name(char *errMsg) \
    { \
    uint8_t result = 0; \
    char *test_name = "" #name "";

#define TESTME_END return result;}

#define TESTME_ASSERT_INT_EQ(a, b) \
    do { \
    if(a != b) \
    { \
    sprintf(errMsg, "%s Assertion Failed: %d != %d\n", test_name, a, b); \
    return 1; \
    } \
    } while(0)

#define TESTME_SUITE(name) \
    int main(void) \
    { \
    char *suite_name = "" #name ""; \
    uint32_t tests_passed = 0, total_tests = 0; \
    struct ErrMsgList head={NULL, NULL}, *tail, *i; \
    tail = &head; \
    char buffer[200]; \
    uint8_t result; \
    printf("Running Test Suite %s.\n", suite_name);

#define TESTME_SUITE_RUN_TEST(name) \
    do { \
    total_tests++; \
    memset(buffer, 0, 200); \
    result = name(buffer); \
    tests_passed += !result; \
    if(result) \
    { \
    tail->next = malloc(sizeof(struct ErrMsgList)); \
    tail = tail->next; \
    tail->next = NULL; \
    tail->msg = malloc(200); \
    strncpy(tail->msg, buffer, 200); \
    printf("F"); \
    } \
    else printf ("."); \
    } while(0)

#define TESTME_SUITE_END \
    printf("\nPassed: %d Total: %d\n", tests_passed, total_tests); \
    for(i=head.next; i; i=i->next) \
    { \
    printf("%s", i->msg);                    \
    } \
    return (tests_passed == total_tests) ? 0 : 1; \
    }

#endif /*TEST_ME*/
