Contributing
============
.. todo::

    Determine official process for verifying and accepting external
    contributions as we advance toward an official release.  For now, please
    contact the development team directly to initiate such collaborations.

Git Workflow
------------
.. _`GitLab`: https://about.gitlab.com/topics/version-control/what-is-gitlab-flow
.. _`GitLab/Japan`: https://docs.gitlab.co.jp/ee/topics/gitlab_flow.html
.. note::

    The specification of this workflow is a work in progress and it is not
    presently in use.  **DON'T WASTE YOUR TIME READING THIS YET, JEFF!**

.. note::

    Even an amazing and well-designed git workflow is useless if PR reviews are
    insufficient and let errors through.

The |poptus| workflow is based on the popular GitLab Flow and the use of
semantic versioning.

* Refer to `GitLab`_ for modern documentation for this base workflow.
* Refer to a `GitLab/Japan`_ document that discusses this base workflow in
  detail and compares it against other well-known workflows.

We use the fact that there are very few package developers, who are also the
gatekeepers, to yield a simple and clean git workflow.  The goal of the workflow
is to ensure that each commit on the ``main`` branch is a mature alteration of
the package that

* has been reviewed,
* is passing all quality checks (|ie| GitHub actions), and
* should be included in the next release.

The workflow also provides users with official releases that correspond to
tagged commits on release branches that have undergone extra reviews for quality
and correctness.

While users should be encouraged to always use the latest official release of
the package, this workflow is designed so that we can simultaneously support bug
fixes on the latest minor release and one or more prior minor releases.

Branches
^^^^^^^^
The repository will use only three types of branches

1. The single infinite lifetime branch ``main``, which should only be committed
   to |via| merge commits/PRs.
2. **Feature branches** that are always based off the latest commit on ``main``
   and that are always merged into ``main`` |via| PRs after careful review by a
   gatekeeper and only if their contents are deemed correct and worthy of
   inclusion in a future release.
3. **Release branches** each of which is associated with a single minor release
   and its patches, is based off of a particular commit in ``main``, contains
   releases as specific commits that are tagged with the associated version
   (``vX.Y.Z``), and
   should never be merged into another branch.

In this sense, the ``main`` branch is conceptually the reasonably clean bleeding
edge of |poptus| development from which polished and trusted official releases
are based.

To maintain a simple and clean commit history on each branch, which should
improve the ease and quality of PR reviews, at any point in time each feature
and each release branch has just one owner.  Another developer is allowed to
commit to a branch only after ownership of the branch has been explicitly
transferred to that person.

If the contents of a feature branch are mature and should be included in a future
release,

  * a PR for pulling the branch into ``main`` should be made;
  * the ``main`` branch should be merged into the feature branch if ``main`` has
    been altered since the feature branch was created so that the two branches
    can be synchronized with integration and merge conflict resolution occurring
    on the feature branch;
  * the developer should perform a self-review of the PR; and
  * a gatekeeper other than the developer should subsequently perform an
    independent review of the PR to accept its inclusion in ``main``.

The size and the scope of each feature branch should be determined by the
developer and the gatekeeper that will perform the PR review.  Ideally it will
be made small enough that the PR review will be quick, easy, and effective.  In
addition, in the spirit of continuous integration priority should be given to
minimizing the number and severity of merge conflicts that could occur during
integration.  However, it should be large enough that gatekeepers aren't swamped
by the overhead of too many tiny PRs.  The naming convention for feature
branches is related to documenting work with Issues and is discussed in a later
section.

.. note::

    Merge conflicts should **never** be resolved using GitHub's web interface
    since this can sometimes cause unitended merging of branches that break this
    workflow.

The creation and management of release branches will be managed on a per-branch
basis by gatekeepers.  Release branches are to be named ``Release_vX.Y``.

.. todo::

    * Describe process for fixing a bug on main and all currently supported
      release branches.

Issues
^^^^^^
Before starting a new feature branch, a pre-existing Issue should be updated or
a new Issue created to document

  * what work will be done on the branch,
  * motivate the need for the work, and
  * capture conversations related to the work.

Since there are many different types of work that can be done on a feature
branch, the contents of Issues can also vary significantly.  Some examples of
Issue documentation are

  * documenting assumptions and design decisions,
  * gathering and improving requirements, as well as
  * documenting the process of identifying, resolving, and determining
    consequences of a bug.

Feature branch names should start with the number of the associated Issue, so
that other developers can easily find all information related to the branch, and
end with a concise summary of the work.  For example, a branch that will carry
out the second step of work requested in Issue 123 could be called
``123StepTwo``.

Since all feature branches are linked to an issue, there is no need to add
further qualifiers to the branch name such as the name of the person that
created the branch or what type of work is being done on the branch (|eg|
feature, bug fix, experimental, documentation, |etc|).

Git Commits
^^^^^^^^^^^
Since the |poptus| software supports methods that are used in scientific
research, both the git commit messages and pull requests should act as
scientific lab notes for recording how the software is characterized, altered,
and verified.

Ideally git commit messages should follow the common best practices of

* Starting with a short first line that provide a useful summary when viewed
  with tools
* Following with one or more paragraphs that do **not** summarize the changes
  made, but rather provide content that cannot be reverse engineered from the
  commits ``diff``.  This can include motivations, assumptions, changes to
  requirements, reasoning, observations, |etc|

To embrace further using messages to capture lab notes, a final paragraph can be
appended that describes what efforts were made to verify the correctness of the
changes.

Pull Requests
^^^^^^^^^^^^^
To help ensure that the contents of a feature branch are good and likely to be
included in a future release, developers are encouraged to open a PR for their
feature branch as soon as possible.  All developer notes and discussions with
the reviewer related to the review and verification of the branch should be
included in that PR.
