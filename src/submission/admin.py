from django.contrib import admin

from .models import (
    HistoryProposal,
    Proposal,
    ProposalReview,
    SubmissionChecklistItem,
)


admin_list = [
    (Proposal,),
    (HistoryProposal,),
    (SubmissionChecklistItem,),
    (ProposalReview,),
]

[admin.site.register(*t) for t in admin_list]
