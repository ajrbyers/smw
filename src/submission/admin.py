from django.contrib import admin

from models import (
    Proposal,
    HistoryProposal,
    SubmissionChecklistItem,
    ProposalReview,
)


admin_list = [
    (Proposal,),
    (HistoryProposal,),
    (SubmissionChecklistItem,),
    (ProposalReview,),
]

[admin.site.register(*t) for t in admin_list]
