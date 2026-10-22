/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left),
 * right(right) {}
 * };
 */
class Solution {
    bool solve(TreeNode* root, int x) {

        if (root == NULL)
            return true;

        bool leftAns = solve(root->left, x);
        bool rightAns = solve(root->right, x);
        return leftAns and root->val == x and rightAns;
    }

public:
    bool isUnivalTree(TreeNode* root) { return solve(root, root->val); }
};