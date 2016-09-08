# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist
from zope.interface import implementer
from openprocurement.api.models import (
    ListType, Feature, Period, get_now,
    validate_features_uniq, validate_lots_uniq,
)
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.flash.models import (
    Auction as BaseAuction, Document as BaseDocument, Bid as BaseBid,
    Complaint as BaseComplaint, Cancellation as BaseCancellation,
    Contract as BaseContract, Award as BaseAward, Lot, edit_role,
)


class Document(BaseDocument):

    documentType = StringType(choices=[
        'auctionNotice', 'awardNotice', 'contractNotice',
        'notice', 'biddingDocuments', 'technicalSpecifications',
        'evaluationCriteria', 'clarifications', 'shortlistedFirms',
        'riskProvisions', 'billOfQuantity', 'bidders', 'conflictOfInterest',
        'debarments', 'evaluationReports', 'winningBid', 'complaints',
        'contractSigned', 'contractArrangements', 'contractSchedule',
        'contractAnnexe', 'contractGuarantees', 'subContract',
        'eligibilityCriteria', 'contractProforma', 'commercialProposal',
        'qualificationDocuments', 'eligibilityDocuments', 'tenderNotice',
        'illustration', 'financialLicense', 'virtualDataRoom',
    ])


class Bid(BaseBid):

    documents = ListType(ModelType(Document), default=list())


class Complaint(BaseComplaint):

    documents = ListType(ModelType(Document), default=list())


class Cancellation(BaseCancellation):

    documents = ListType(ModelType(Document), default=list())


class Contract(BaseContract):

    documents = ListType(ModelType(Document), default=list())


class Award(BaseAward):
    complaints = ListType(ModelType(Complaint), default=list())
    documents = ListType(ModelType(Document), default=list())


def validate_not_available(items, *args):
    if items:
        raise ValidationError(u"Option not available in this procurementMethodType")


@implementer(IAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = {
            'edit_active.tendering': (blacklist('enquiryPeriod', 'tenderPeriod', 'value', 'auction_value', 'minimalStep', 'guarantee', 'auction_guarantee') + edit_role),
        }

    awards = ListType(ModelType(Award), default=list())
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    enquiryPeriod = ModelType(Period)  # The period during which enquiries may be made and will be answered.
    procurementMethodType = StringType(default="dgfOtherAssets")
    status = StringType(choices=['draft', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    features = ListType(ModelType(Feature), validators=[validate_features_uniq, validate_not_available])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq , validate_not_available])

    def initialize(self):
        if not self.enquiryPeriod:
            self.enquiryPeriod = type(self).enquiryPeriod.model_class()
        if not self.enquiryPeriod.startDate:
            self.enquiryPeriod.startDate = self.tenderPeriod.startDate or get_now()
        if not self.enquiryPeriod.endDate:
            self.enquiryPeriod.endDate = self.tenderPeriod.endDate
        if not self.tenderPeriod.startDate:
            self.tenderPeriod.startDate = self.enquiryPeriod.startDate
        now = get_now()
        self.date = now
        if self.lots:
            for lot in self.lots:
                lot.date = now

    def validate_tenderPeriod(self, data, period):
        pass