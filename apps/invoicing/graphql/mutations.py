from KlimaKar.graphql.resolvers import BaseModelFormResolver
from apps.invoicing.forms import ContractorModelForm
from apps.invoicing.models import Contractor

from apps.commission.graphql.types import mutation


class AddContractorResolver(BaseModelFormResolver):
    form_class = ContractorModelForm


@mutation.field("addContractor")
def resolve_add_contractor(_, info, data):
    return AddContractorResolver(data).process()


@mutation.field("updateContractor")
def resolve_update_contractor(_, info, id, data):
    instance = Contractor.objects.get(pk=id)
    return AddContractorResolver(data, instance).process()
