---
layout: blog
title: "Starting a Nonprofit in DC"
author: Steven Reilly and Matt Bailey
authors:
- stvnrlly
- mbailey
date: 2016-11-17 16:12:01
categories: blog
description: "Our step-by-step plan for becoming a nonprofit"
---

One of our goals for this year is turning Code for DC into a nonprofit organization. We think that this will allow us to do some cool new stuff, in addition to our traditional hacknight, such as creating a civic user testing group, managing our nascent data portal, serving as a fiscal sponsor to other similarly-minded groups, and generally having more transparency around our finances.

The task has seemed daunting and progress towards it has only come in fits and starts. The basic obstacle: the application process—particularly with the District—isn’t entirely clear, which makes it difficult to see the plan from start to finish.

So, recently, we sat down and tried to put the pieces together into a coherent plan. While we aren’t sure we’ve got the steps right—or that we’ve got them all—we thought we’d share what we’ve learned now in the hopes that it can help others along the way. We’re also hoping to shine a little light on the unnecessary barriers that poor documentation of the process are throwing up for community organizations in DC.

Here's the process, as we understand it so far.

<!--more-->

## Parallel processing


One of the things that makes this process extra fun is that it involves both federal and local agencies. The processes sort of leap-frog each other, so there’ll be a bit of back and forth. For example, filing the federal IRS form 1023 requires incorporation with your local government. Also, filing the local OTR form 500 requires getting an Employer Identification Number from the IRS. The Free Law Project (FLP) went through this process a couple years ago in California and [wrote up their steps](http://michaeljaylissner.com/posts/2014/10/14/becoming-a-non-profit/), which seem to confirm this flow.

In very broad strokes, you’ll (1) register a corporate entity separately with DC and the federal government, then (2) using some information from that step, apply for tax exemption from DC and the federal government. The exact process varies state by state, although there are a lot of similarities, so people outside DC may still find the overarching themes and federal parts useful.

## Overview

Having gotten through the up front questions of where to start, we spent some time figuring out what seem to be the main steps in the DC-specific process.

At first, the process appeared to involve three separate DC agencies:

- the Department of Consumer and Regulatory Affairs (DCRA),
- the Office of the Deputy Mayor for Planning and Economic Development (DMPED), and
- the Office of Tax and Revenue (OTR)

Both DCRA and DMPED have pages about creating a nonprofit. [The DCRA
page](http://dcra.dc.gov/service/register-and-license-non-profit-organization)
covers the main steps, while [the DMPED page](http://dmped.dc.gov/node/814892)
covers overarching questions and tasks, some of which overlap with DCRA steps.
This caused us some confusion at first because it was unclear how the pages related to
each other. But since a registrant files the form with DCRA, that seems like the primary one.

That sorted, these seem to be the main points:

1. Organize your information and prep basic materials
  - Draft your mission statement
  - Draft your articles of incorporation
  - Draft your bylaws
  - Plan out the Board of Directors
  - Determine the initial officers
  - Get a registered agent
  - Figure out your office
  - Determine whether you'll need a business license
1. Get an Employer Identification Number from the IRS
1. File the Articles of Incorporation with DC Form DNP-1
1. File tax stuff with the IRS
  - File for an exemption with IRS Form 1023
1. File tax stuff with DC
  - Register with OTR with DC Form 500
  - File for an exemption with DC Form 164
1. Get a Basic Business License, maybe
1. ...non-profit?

Here’s what we think we know about each one.

## 1. Organize your information and prep other basic materials

### Draft your mission statement

This is not specifically a required step as it is not a legal document and is never filed with anybody as part of this process, but it is a useful exercise for ironing out your vision and producing some content that will come in handy as you fill out forms again and again. It will also be really helpful in explaining your organization to potential partners, funders, and the like in the future. The mission statement should be short and to the point.

### Draft Articles of Incorporation

These will be submitted later, but you should probably do it now. The Articles of Incorporation describe your non-profit in formal language at a high level. They're relatively short and hit a few key points that DC's Superintendent of Corporations cares about. You'll get to use that mission statement here.

The IRS provides some ["suggested language" for this document](https://www.irs.gov/charities-non-profits/suggested-language-for-corporations-and-associations), which has the basics of what is needed. Additionally, both the [DC Open Government Coalition](http://www.dcogc.org/content/articles-incorporation) and [the OpenGov Foundation](https://github.com/opengovfoundation/legal-information/blob/master/dc-certificate-of-incorporation.pdf) have posted their articles, which you can use as a reference. The OpenGov Foundation’s are included as part of their certificate of incorporation, which you’ll receive back after filing DC Form DNP-1.

You may notice that both examples include a fair amount more than is suggested by the IRS. While only a few basics are needed, the articles of incorporation are your opportunity to give direction to the organization. Contrast these to the bylaws, which govern how the officers and directors carry out that direction. The bylaws can be amended by a simple vote of the board, while the articles must be amended by filing formal paperwork (DC Form DNP-2, in case you're wondering) with DC.

For technology-minded groups: note that things like “open source” have popped up in the past as phrases that cause the IRS to give an application extra scrutiny, which could delay the process indefinitely. The EFF has [a good explanation](https://www.eff.org/deeplinks/2014/07/open-source-madness) on the issue.

### Draft bylaws

These will also come into play later, but are good to create now rather than in a rush once the organization is already up and running. The bylaws set forth the actual rules for operation of the organization, and thus set the tenor for the overall function. As before, you can use the [OpenGov Foundation's
bylaws](https://github.com/opengovfoundation/legal-information/blob/master/bylaws.md)
as a guide, but note that they have both a Board of Directors and a Board of Advisors, the latter of which may not be relevant for you.

As part of this step, you'll also have to consider whether your organization will have "members". This doesn’t have the same meaning we usually give it in describing participants in community organizations. Instead it has the specific legal meaning of somebody who votes in the election of directors and things like that. [D.C. Code § 29-401.02(24)](https://beta.code.dccouncil.us/dc/council/code/sections/29-401.02.html).
Having members is not required to form a nonprofit. [D.C. Code § 29-404.01(a)
](https://beta.code.dccouncil.us/dc/council/code/sections/29-404.01.html). We
decided that we probably do not need members, but other organizations may find
them useful.

### Plan out the Board of Directors

This is listed as "establishing" a board of directors in a variety of places, but that seems difficult to do before the organization actually exists. Instead, we think this means that you should contact people and line them up to join the Board as soon as it is possible. You'll need to have at least three of them. [D.C. Code § 29-406.03(a)](https://beta.code.dccouncil.us/dc/council/code/sections/29-406.03.html).

### Determine initial officers

These are the people who will carry out the corporate nonprofit stuff once the organization is formed. As we understand it,[^1] they aren’t usually members of the Board but work with the Board very closely. They are _likely_ to be the people doing the incorporating, but you should work out who will have which role. A nonprofit in DC is required to have at least a President and a Treasurer, though you can create more if it's useful. [D.C. Code §
29-406.40(a)](https://beta.code.dccouncil.us/dc/council/code/sections/29-406.40.html).

[^1]: We couldn't tell immediately if Officers can technically also be Directors. It seems like they can be, and while some Officers might also be Directors there should probably be Directors who are not Officers.

### Get a registered agent

A registered agent is basically a human who makes themself available to receive mail-type things on behalf of the corporation. This step is not mentioned anywhere on either the DCRA or DMPED site, but is a required element of DCRA Form DNP-1 (more on that below). DCRA provides more information on a [registered agent page](http://dcra.dc.gov/service/corporate-registration-registered-agent) and a [set of forms](http://dcra.dc.gov/sites/default/files/dc/sites/dcra/publication/attachments/RA-1-7.pdf),
but it's not super clear who can fill this role.

Under DC law, there are two types of registered agents: commercial and noncommercial.  However, the set of forms only includes a registration form for commercial agents. This makes it *seem* like somebody like one of us could serve as a noncommercial registered agent for an organization just by documenting it in our paperwork[^2], but it's also possible that that's an incorrect reading of [D.C. Code §
29.104.04](https://beta.code.dccouncil.us/dc/council/code/sections/29-104.04.html).

[^2]: It seems like the benefit of a commercial registered agent is likely that there’s a buffer between the people and the corporation, but this may not be worth the expense/hassle if you are small.

### Figure out your office

This is listed as one of the last steps on the DCRA site, but it seems good to know up front. First of all, don’t freak out: you don’t need to take out a lease in order to start a nonprofit in DC. What you do need is an address where the nonprofit can be registered to, similar to how your personal tax records require you to fill out an address. It looks like this can be a commercial building with a Certificate of Occupancy or a home with a Home Occupation Permit. We’re still deciding what address to use but it will probably be someone’s personal residence.

A remaining question: what all is involved in applying for a Home Occupation Permit and how long should we expect it to take?

### Determine whether you'll need a business license

This is also listed as one of the last steps on the DCRA site, but likewise seems good to know up front.

DCRA doesn't provide any real information about this in the guide, advising registrants to instead contact the Business Licensing Division by phone. As a result, we have no idea what sort of calculus goes into determining whether or not a license is required. :-|
A remaining question: do we need a business license?

## 2. Get an Employer Identification Number from the IRS

The organization might not plan to actually employ anybody, but it'll still need an EIN. This is essentially the Social Security Number of organizations. You can apply for an EIN through [IRS Form SS-4](https://www.irs.gov/pub/irs-pdf/fss4.pdf) or [online](https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online).

As discussed below, this is earlier than some of the forms recommend. This is probably fine, as you have 27 months after that EIN trigger to file for an exemption. We're following the FLP's lead here, who got an EIN before incorporating in California.

## 3. File the Articles of Incorporation with DCRA Form DNP-1

Cost: $80.00

Now that you’ve assembled your materials, DNP-1 is the main form you file with the District to establish a non-profit at the State level. The form isn't actually linked from the DCRA page, but can [easily be
found](http://dcra.dc.gov/sites/default/files/dc/sites/dcra/publication/attachments/Articles%20of%20Incorporation%20of%20Domestic%20Nonprofit%20Corporation%20DNP-1.pdf) by searching. Although neither of the checklists mentions it, you can also [file the DNP-1 online](http://dcra.dc.gov/service/domestic-nonprofit-corporation). It might be worth creating that CorpOnline account, as that also seems to be a method for filing the [biennial reporting requirement](http://dcra.dc.gov/sites/default/files/dc/sites/dcra/page_content/attachments/Two-Year%20Report%20for%20Domestic%20%26%20Foreign%20Filing%20Entity%20BRA-25.pdf).

One potentially confusing thing here is that DNP-1 asks you to state that “the corporation is incorporated as a nonprofit corporation under Title 29 Chapter 4”, which is a reference to [the definition in DC Code of a non-profit](https://beta.code.dccouncil.us/dc/council/code/titles/29/chapters/4/subchapters/IV/). This threw us for a loop, as we figured that it wouldn’t be a “non-profit” until we filed for tax exemption. However, while the terms are often used interchangeably, a non-profit corporation can operate without tax exempt status. While it’s not common, it is possible. (Imagine, for example, that a non-profit loses its tax exempt status for some kind of bad behavior: it is still a non-profit, but no longer tax exempt.)

## 4. File tax stuff with the IRS

It's a bit unclear what order things are supposed to happen in here. This is the text on DC's OTR site:

> While you may already be registered as a non-profit with the Internal Revenue Service (IRS), and if you're not you'll need to do this first, to do business in the District of Columbia you'll also need to register with District of Columbia Office of Tax and Revenue (OTR).

While this is in an [IRS publication on 501(c)(3) status](https://www.irs.gov/pub/irs-pdf/p4220.pdf):

> Do not apply for an EIN until your organization is legally formed. Applying for an EIN signals to IRS computer systems that an organization has been created, and therefore triggers filing requirements.

We think that "legally formed" means that you've gotten your certificate of incorporation back from DCRA based on your DNP-1 filing, so this would be the _most correct_ place for this step, but since you'll have already completed it back when you were working on the DNP-1.

### File for an exemption

Cost: $275.00

Now that you have an EIN, you can file for exempt status. The [IRS publication](https://www.irs.gov/pub/irs-pdf/p4220.pdf) quoted above is a decent primer, and there are also legal-ish [instructions for Form 1023](https://www.irs.gov/pub/irs-pdf/i1023.pdf). However, if you don't expect to receive more than $50,000 in any of the next 3 years, you can file [Form 1023-EZ](https://www.irs.gov/uac/about-form-1023ez) instead. It appears that you can only file the 1023-EZ online, and can only access it by searching for it on [pay.gov](https://pay.gov/).

## 5. File tax stuff with DC

This portion of the process is managed by DC's Office of Tax and Revenue. As with DNP-1, the forms aren't actually linked from the DCRA guide, but can be found quickly. [Form 500](http://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/48225_FR-500_81315.pdf) is the form to register with the office, and [Form 164](http://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/fr-164_rev12-07_application_package.pdf) is the form to apply for the tax exemption.

Form 500 has a bunch of elements, and initially seems like things that a normal person would have no idea, but the instructions are pretty good. The three pages of "Codes for Principal Activity" are quite daunting, but luckily we think we fall into the `813000` catch-all category of "Religious, Grantmaking, Civic, Professional, & Similar Organizations (including condominium and homeowners associations)". In case you're curious, these codes are the NAICS codes used by the federal government to categorize businesses. It initially seems like you have to print the form out and mail it in, but thankfully there is [an online system](https://mytax.dc.gov/) for it.

Form 164 is weirder and is typeset with some sort of typewriter font that makes it hard to read, but seems relatively straightforward. It requires you to specify the end of your annual accounting period, and we don't know whether that makes any sort of difference. It also asks for "Physical Location(s) of Personal Property in the District", which may or may not be related to the registered agent. There's a $70 fee for out-of-state organizations, but no mention of a fee for DC organizations.

Another side note: every DC form in this process looks different. This isn't a huge deal, but there is a psychological cost to the registrant in needing to figure out how to approach each of these forms.

## 6. Get a Basic Business License, maybe

If you determined earlier that this is necessary, do it here.

According to the [DCRA BBL Fact
Sheet](http://dcra.dc.gov/sites/default/files/dc/sites/dcra/publication/attachments/5%20Basic%20Steps%20to%20Opening%20a%20Business%20Handout%20Final.pdf), most of the steps should be completed by this point. There's a fee of at least $95 for this, though there's another $200 fee that seems to be for certain categories of business. It's not super clear.

## 7. That's It?

The only thing left after this point is to operate the organization in full compliance with all applicable laws and regulations!

As noted above, we're at the very beginning of this process, and are using this post to work out a plan of action. We will do our best to update it as our information improves, but please do not mistake this for the advice of an expert.
